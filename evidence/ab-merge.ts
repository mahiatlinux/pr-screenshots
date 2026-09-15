import assert from "node:assert/strict";
import test from "node:test";
import ts from "/task/merge/studio/frontend/node_modules/typescript/lib/typescript.js";
import { readFileSync } from "node:fs";
const readSrc = (p: string) => readFileSync("/task/merge/studio/frontend/src/"+p,"utf8");
import {
  localPromptQueueModelBoundary,
  shouldAbortPendingQueueForModelBoundary,
  shouldAbortPendingQueueForSettingsChange,
} from "/task/merge/studio/frontend/src/features/chat/utils/prompt-queue-model-boundary.ts";
import { snapshotQueuedChatRunSettings } from "/task/merge/studio/frontend/src/features/chat/utils/queued-chat-run-settings.ts";
import { reorderPromptQueueItems } from "/task/merge/studio/frontend/src/features/chat/utils/prompt-queue-reorder.ts";
import { steeringInsertionIndex } from "/task/merge/studio/frontend/src/features/chat/utils/composer-preferences.ts";
import { chatModelLifecycleGate } from "/task/merge/studio/frontend/src/features/chat/utils/model-lifecycle-gate.ts";
import { parseExternalModelId } from "/task/merge/studio/frontend/src/features/chat/external-providers.ts";
import {
  planUserPromptQueueStop,
  userStopTargetCancelMode,
} from "/task/merge/studio/frontend/src/features/chat/utils/prompt-queue-user-stop.ts";

// Run the production queue engine with controlled stores and transport.
const source = ts.createSourceFile(
  "thread.tsx",
  readSrc("components/assistant-ui/thread.tsx"),
  ts.ScriptTarget.Latest,
  true,
  ts.ScriptKind.TSX,
);
const names = [
  "startPromptQueue",
  "steerPromptQueueTarget",
  "steerPromptQueueItem",
  "findPromptQueueRunByItemId",
  "pausePromptQueueRun",
  "resumePromptQueueRun",
  "getPromptQueueRunsForThreadIds",
  "getActivePromptQueueItem",
  "createQueuedPrompt",
  "getPromptQueueTargetIds",
  "getPromptQueueRunTargetIds",
  "promptQueueRunMatchesThreadIds",
  "findPromptQueueRunByTarget",
  "findPromptQueueRunByThreadIds",
  "isPromptQueueTargetRunning",
  "isActivePromptQueueItem",
  "dispatchQueuedPrompt",
  "isPromptQueueRunReadyToDispatch",
  "handlePromptQueueRunState",
  "isPromptQueueRunTargetRunning",
  "advancePromptQueue",
  "handlePromptQueueRunFailed",
  "retainPendingPromptQueueItemsAfterFailure",
];
const declarations = names
  .map((name) => {
    const node = source.statements.find(
      (node) => ts.isFunctionDeclaration(node) && node.name?.text === name,
    );
    assert.ok(node, `Missing production function ${name}`);
    return node.getText(source);
  })
  .join("\n");
const js = ts.transpileModule(declarations, {
  compilerOptions: {
    target: ts.ScriptTarget.ES2022,
    module: ts.ModuleKind.None,
  },
}).outputText;

type Target = ReturnType<typeof makeTarget>;
type Item = { id: string; prompt: string; target: Target; dispatched: boolean };
type Run = {
  id: string;
  items: Item[];
  index: number;
  generation: number;
  paused: boolean;
  waitingForTargetIdle: boolean;
};
function makeTarget(id: string, running = true) {
  return {
    getRunningThreadIds: () => (id ? [id] : []),
    getDocumentThreadId: () => id || null,
    running,
    usesLocalModel: true,
    researchStarted: () => false,
    complete: () => undefined,
    cancels: 0,
    permanentCancels: 0,
    deepResearch: 0,
    isRunning() {
      return this.running;
    },
    cancelActiveRun() {
      this.cancels += 1;
    },
    cancel() {
      this.permanentCancels += 1;
    },
    consumeDeepResearch() {
      this.deepResearch += 1;
    },
  };
}
function world() {
  const runs = new Map<string, Run>();
  const appended: string[] = [];
  const scopedCancels: string[][] = [];
  let serial = 0;
  let modelLoading = false;
  let dispatchRetries = 0;
  let indexing: () => Promise<boolean> = async () => false;
  const noop = () => undefined;
  const deps = {
    promptQueueRuns: runs,
    promptQueueRunOrder: [],
    promptQueueActiveRunIds: new Set(),
    promptQueueDispatchingRunIds: new Set(),
    compactIds: (ids: unknown[]) => [...new Set(ids.filter(Boolean))],
    createPromptQueueRunId: () => `run-${++serial}`,
    createPromptQueueItemId: () => `item-${++serial}`,
    planUserPromptQueueStop,
    userStopTargetCancelMode,
    steeringInsertionIndex,
    cancelPreStreamRunForThreadIds: (ids: string[]) => scopedCancels.push(ids),
    useChatRuntimeStore: {
      getState: () => ({ runningByThreadId: {}, modelLoading }),
    },
    syncPromptQueueUI: noop,
    ensurePromptQueueSubscription: noop,
    requestPromptQueuePump: noop,
    requestPromptQueuePumpIfReady: noop,
    clearPromptQueueRetryTimer: noop,
    schedulePromptQueueTargetStatePoll: noop,
    scheduleQueuedPromptDispatch: () => {
      dispatchRetries += 1;
    },
    PROMPT_QUEUE_DISPATCH_RETRY_MS: 500,
    PROMPT_QUEUE_INDEXING_RETRY_MS: 1,
    deletePromptQueueRun: (run: Run) => runs.delete(run.id),
    toast: { info: noop },
    discardQueuedChatRunSettingsForThread: noop,
    targetHasIndexingDocuments: () => indexing(),
    appendQueuedPrompt: (_run: Run, item: Item) => {
      appended.push(item.prompt);
      item.dispatched = true;
    },
  };
  const engine = new Function(
    ...Object.keys(deps),
    `${js}\nreturn {startPromptQueue, steerPromptQueueItem, dispatchQueuedPrompt, isPromptQueueRunReadyToDispatch, handlePromptQueueRunState, handlePromptQueueRunFailed, resumePromptQueueRun};`,
  )(...Object.values(deps)) as {
    handlePromptQueueRunFailed: (
      threadId?: string,
      localOnly?: boolean,
    ) => void;
    resumePromptQueueRun: (threadIds?: string[]) => void;
    startPromptQueue: (
      items: string[],
      target: Target,
      wait?: boolean,
      behavior?: "queue" | "steer",
    ) => void;
    steerPromptQueueItem: (id: string) => boolean;
    dispatchQueuedPrompt: (
      run: Run,
      item: Item,
      generation?: number,
    ) => Promise<void>;
    isPromptQueueRunReadyToDispatch: (run: Run) => boolean;
    handlePromptQueueRunState: (
      run: Run,
      runningByThreadId: Record<string, boolean>,
    ) => void;
  };
  return {
    ...engine,
    runs,
    appended,
    scopedCancels,
    setModelLoading: (loading: boolean) => {
      modelLoading = loading;
    },
    dispatchRetries: () => dispatchRetries,
    setIndexing: (probe: () => Promise<boolean>) => {
      indexing = probe;
    },
    run: () => [...runs.values()][0]!,
  };
}

function composerCallbackJs(name: string) {
  let factory: ts.Expression | undefined;
  function visit(node: ts.Node) {
    if (
      ts.isVariableDeclaration(node) &&
      node.name.getText(source) === name &&
      node.initializer &&
      ts.isCallExpression(node.initializer)
    ) {
      factory = node.initializer.arguments[0];
    }
    ts.forEachChild(node, visit);
  }
  visit(source);
  assert.ok(factory, `Missing production callback ${name}`);
  return ts.transpileModule(`return (${factory.getText(source)});`, {
    compilerOptions: {
      target: ts.ScriptTarget.ES2022,
      module: ts.ModuleKind.None,
    },
  }).outputText;
}
const factoryJs = composerCallbackJs("startHydratedPromptQueue");
const targetFactoryJs = composerCallbackJs("createPromptQueueTarget");

async function targetForSelection(checkpoint: string, modelLoading: boolean, incoming: string | null) {
  let settings!: ReturnType<typeof snapshotQueuedChatRunSettings>;
  const runtime = {
    params: { checkpoint, temperature: 0.4 },
    activeGgufVariant: "old-Q4.gguf",
    loadingModelPick: incoming ? { id: incoming } : null,
    modelLoading,
    permissionMode: "ask",
    toolsEnabled: true,
    ragEnabled: false,
    incognito: false,
    hydratePersistedSettings: async () => undefined,
  };
  const deps = {
    aui: {
      threads: () => ({}),
      threadListItem: () => ({ getState: () => ({ id: "chat", remoteId: "chat" }) }),
    },
    referenceThreadId: "chat",
    chatHistoryClearBoundary: { capture: () => 0 },
    promptQueueTargetMountedRef: { current: true },
    indexingActiveRef: { current: false },
    useChatRuntimeStore: { getState: () => runtime },
    compactIds: (ids: unknown[]) => [...new Set(ids.filter(Boolean))],
    snapshotQueuedChatRunSettings: (...args: Parameters<typeof snapshotQueuedChatRunSettings>) => {
      settings = snapshotQueuedChatRunSettings(...args);
      return settings;
    },
    parseExternalModelId,
    hasPreStreamRunReservation: () => false,
  };
  const create = new Function(...Object.keys(deps), targetFactoryJs)(
    ...Object.values(deps),
  ) as () => Promise<Target>;
  return { target: Object.assign(makeTarget("chat", false), await create()), settings };
}

function hydratedFactory(
  w: ReturnType<typeof world>,
  target: Target,
  hydrate = () => Promise.resolve(target),
) {
  const pending = new Map();
  const deps = {
    referenceThreadId: "chat",
    promptQueueStartPendingRef: { current: pending },
    pendingQueueStartIsStale: () => false,
    useChatRuntimeStore: {
      getState: () => ({
        modelLoading: true,
        queuedSettingsEpoch: 0,
        incognito: false,
      }),
    },
    localPromptQueueModelBoundary,
    shouldAbortPendingQueueForModelBoundary,
    shouldAbortPendingQueueForSettingsChange,
    createPromptQueueTarget: hydrate,
    startPromptQueue: w.startPromptQueue,
    toast: { error: (message: string) => assert.fail(message) },
  };
  return new Function(...Object.keys(deps), factoryJs)(
    ...Object.values(deps),
  ) as (
    prompts: string[],
    wait: boolean,
    onStarted?: () => void,
    onAborted?: () => void,
    capturedAt?: {
      localModelBoundaryGeneration: number;
      queuedSettingsEpoch: number;
      temporary: boolean;
    },
    behavior?: "queue" | "steer",
  ) => boolean;
}

test("three follow-ups are accepted and reorderable during loading, then dispatch in order after the first response", async () => {
  const w = world();
  w.setModelLoading(true);
  const target = makeTarget("chat");
  const accept = hydratedFactory(w, target);
  const cleared: string[] = [];
  for (const text of ["second", "third", "fourth"]) {
    assert.equal(
      accept([text], true, () => cleared.push(text)),
      true,
    );
  }
  await Promise.resolve();
  console.log("accepted", cleared.length);
  assert.deepEqual(
    cleared,
    ["second", "third", "fourth"],
    "the composer clears each accepted prompt so another can be entered",
  );
  const run = w.run();
  assert.deepEqual(
    run.items.map((i) => i.prompt),
    cleared,
  );
  assert.ok(run.items.every((i) => !i.dispatched));
  assert.equal(run.index, -1);
  run.items = reorderPromptQueueItems(run.items, 2, 0)!;
  assert.deepEqual(
    run.items.map((i) => i.prompt),
    ["fourth", "second", "third"],
  );
  await w.dispatchQueuedPrompt(run, run.items[0]);
  assert.deepEqual(w.appended, []);
  assert.equal(w.dispatchRetries(), 1);
  w.setModelLoading(false);
  w.handlePromptQueueRunState(run, {});
  assert.equal(
    run.index,
    -1,
    "finishing the model load must not skip the first response",
  );
  target.running = false;
  w.handlePromptQueueRunState(run, {});
  assert.equal(run.index, 0);
  for (const text of ["fourth", "second", "third"]) {
    const item: Item = run.items[run.index];
    assert.equal(item.prompt, text);
    await w.dispatchQueuedPrompt(run, item);
    target.running = true;
    w.handlePromptQueueRunState(run, {});
    target.running = false;
    w.handlePromptQueueRunState(run, {});
  }
  assert.deepEqual(w.appended, ["fourth", "second", "third"]);
  assert.equal(w.runs.size, 0);
});


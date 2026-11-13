"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const { run, branchKind, targets, nextPatch } = require("./gitflow.cjs");

function fake(names, options = {}) {
  const branches = Object.fromEntries(["main", "develop", ...names].map(name => [name, { sha: `${name}-sha`, included: new Set() }]));
  const prs = options.prs ?? [];
  const tags = new Map((options.tags ?? []).map(name => [name, "previous-main"]));
  const merges = [];
  const created = [];
  const deleted = [];
  let attempts = 0;
  const error = status => Object.assign(new Error(`HTTP ${status}`), { status });
  const api = {
    repos: {
      listBranches: async () => Object.entries(branches).map(([name, value]) => ({ name, commit: { sha: value.sha } })),
      getBranch: async ({ branch }) => {
        if (!branches[branch]) throw error(404);
        return { data: { name: branch, commit: { sha: branches[branch].sha } } };
      },
      compareCommitsWithBasehead: async ({ basehead }) => {
        const [base, sha] = basehead.split("...");
        return { data: { ahead_by: branches[base].included.has(sha) || branches[base].sha === sha ? 0 : 1 } };
      },
      listTags: async () => [...tags].map(([name, sha]) => ({ name, commit: { sha } })),
    },
    pulls: {
      list: async ({ head, base }) => prs.filter(pr => pr.head.ref === head.split(":")[1] && pr.base.ref === base).slice().reverse(),
      create: async args => {
        const pr = { number: prs.length + 1, body: args.body, state: "open", draft: args.draft, merged_at: null, mergeable: options.conflict ? false : true, html_url: `https://github.test/pr/${prs.length + 1}`, head: { ref: args.head, sha: branches[args.head].sha }, base: { ref: args.base } };
        prs.push(pr); created.push(pr); return { data: pr };
      },
      update: async ({ pull_number, body }) => { const pr = prs.find(pr => pr.number === pull_number); pr.body = body; return { data: pr }; },
      get: async ({ pull_number }) => {
        const pr = prs.find(pr => pr.number === pull_number);
        if (options.moveHead) { branches[pr.head.ref].sha = "new-head"; pr.head.sha = "new-head"; }
        return { data: pr };
      },
      merge: async ({ pull_number, sha, merge_method }) => {
        attempts++;
        assert.equal(merge_method, "merge");
        if (options.transient && attempts === 1) throw error(503);
        const pr = prs.find(pr => pr.number === pull_number);
        assert.equal(sha, branches[pr.head.ref].sha);
        const target = branches[pr.base.ref];
        target.sha = `merged-${pull_number}`;
        target.included.add(sha);
        for (const ancestor of branches[pr.head.ref].included) target.included.add(ancestor);
        pr.state = "closed"; pr.merged_at = "2026-11-13"; pr.merge_commit_sha = target.sha;
        merges.push([pr.head.ref, pr.base.ref, sha]);
        if (options.lostResponse && attempts === 1) throw error(503);
        return { data: { merged: true, sha: target.sha } };
      },
    },
    git: {
      getRef: async ({ ref }) => { if (!tags.has(ref.slice(5))) throw error(404); return { data: { object: { type: "commit", sha: tags.get(ref.slice(5)) } } }; },
      createRef: async ({ ref, sha }) => { assert(!tags.has(ref.slice(10))); tags.set(ref.slice(10), sha); },
      deleteRef: async ({ ref }) => { const name = ref.slice(6); deleted.push(name); delete branches[name]; },
    },
  };
  const args = { github: { rest: api, paginate: async (method, args) => method(args) }, context: { repo: { owner: "equipo", repo: "proyecto" } }, core: { info() {} }, sleep: async () => {} };
  return { args, branches, prs, tags, merges, created, deleted };
}

test("clasifica las ramas y conserva Gitflow", () => {
  assert.equal(branchKind("main"), null);
  assert.equal(branchKind("release/no-version"), null);
  assert.deepEqual(targets("feature/ui", []), ["develop"]);
  assert.deepEqual(targets("release/0.1.0", []), ["main", "develop"]);
  assert.deepEqual(targets("hotfix/red", ["release/1.1.0"]), ["main", "develop", "release/1.1.0"]);
  assert.equal(nextPatch([{ name: "v1.9.9" }, { name: "v1.10.2" }, { name: "otro" }]), "v1.10.3");
  assert.throws(() => nextPatch([]), /versión publicada/);
});

test("crea un PR de funcionalidad y lo integra sin aprobación", async () => {
  const f = fake(["feature/ui"]);
  await run(f.args);
  assert.deepEqual(f.merges.map(item => item.slice(0, 2)), [["feature/ui", "develop"]]);
  assert.deepEqual(f.deleted, ["feature/ui"]);
  await run(f.args);
  assert.equal(f.created.length, 1);
});

test("reutiliza un PR existente sin duplicarlo", async () => {
  const f = fake(["feature/ui"]);
  await f.args.github.rest.pulls.create({ head: "feature/ui", base: "develop", draft: false, body: "Descripción humana" });
  await run(f.args);
  assert.equal(f.created.length, 1);
  assert.equal(f.prs[0].body, "Descripción humana");
});

test("publica la release, la etiqueta y el retorno a develop en una ejecución", async () => {
  const f = fake(["release/0.1.0"]);
  await run(f.args);
  assert.deepEqual(f.merges.map(item => item[1]), ["main", "develop"]);
  assert.equal(f.tags.get("v0.1.0"), "merged-1");
  assert.match(f.prs[0].body, /gitflow-version:v0.1.0/);
});

test("el hotfix retorna también a la release activa", async () => {
  const f = fake(["hotfix/red", "release/1.1.0"], { tags: ["v1.0.0"] });
  await run(f.args);
  assert.deepEqual(f.merges.filter(item => item[0] === "hotfix/red").map(item => item[1]), ["main", "develop", "release/1.1.0"]);
  assert.equal(f.tags.get("v1.0.1"), "merged-1");
});

test("reintenta un fallo transitorio", async () => {
  const f = fake(["feature/ui"], { transient: true });
  await run(f.args);
  assert.equal(f.created.length, 1); assert.equal(f.merges.length, 1);
});

test("reconcilia una respuesta perdida sin repetir el merge", async () => {
  const f = fake(["release/0.1.0"], { lostResponse: true });
  await run(f.args);
  assert.equal(f.merges.length, 2);
  assert.equal(f.tags.get("v0.1.0"), "merged-1");
});

test("conserva las ramas previamente integradas al activar el controlador", async () => {
  const f = fake(["feature/anterior"]);
  f.branches.develop.included.add("feature/anterior-sha");
  await run(f.args);
  assert.equal(f.merges.length, 0); assert.equal(f.created.length, 0); assert.equal(f.deleted.length, 0);
});

test("informa conflictos y conserva el origen", async () => {
  const f = fake(["feature/ui"], { conflict: true });
  await assert.rejects(run(f.args), /Conflictos en PR #1/);
  assert.equal(f.merges.length, 0); assert.equal(f.deleted.length, 0);
});

test("rechaza un cambio de SHA antes del merge", async () => {
  const f = fake(["feature/ui"], { moveHead: true });
  await assert.rejects(run(f.args), /origen del PR #1 cambió/);
  assert.equal(f.merges.length, 0);
});

test("no sobrescribe una etiqueta de otra entrega", async () => {
  const f = fake(["release/0.1.0"], { tags: ["v0.1.0"] });
  await assert.rejects(run(f.args), /etiqueta v0.1.0 ya existe/);
  assert.equal(f.merges.length, 0);
});

test("mantiene la versión de hotfix registrada en el PR", async () => {
  const f = fake(["hotfix/red"], { tags: ["v2.0.0"] });
  await f.args.github.rest.pulls.create({ head: "hotfix/red", base: "main", draft: false, body: "Corrección\n<!-- gitflow-version:v1.0.1 -->" });
  await run(f.args);
  assert.equal(f.tags.get("v1.0.1"), "merged-1");
});

test("conserva un PR marcado explícitamente como borrador", async () => {
  const f = fake(["feature/ui"]);
  await f.args.github.rest.pulls.create({ head: "feature/ui", base: "develop", draft: true, body: "En preparación" });
  await assert.rejects(run(f.args), /está en borrador/);
  assert.equal(f.merges.length, 0);
});

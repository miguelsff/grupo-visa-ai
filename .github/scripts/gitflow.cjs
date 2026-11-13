"use strict";

const VERSION = /^v?(\d+)\.(\d+)\.(\d+)$/;
const MARKER = /<!-- gitflow-version:(v\d+\.\d+\.\d+) -->/;

function branchKind(name) {
  if (name.startsWith("feature/")) return "feature";
  if (/^release\/\d+\.\d+\.\d+$/.test(name)) return "release";
  if (name.startsWith("hotfix/")) return "hotfix";
  return null;
}

function targets(name, releases) {
  const kind = branchKind(name);
  if (kind === "feature") return ["develop"];
  if (kind === "release") return ["main", "develop"];
  if (kind === "hotfix") return ["main", "develop", ...releases];
  return [];
}

function nextPatch(tags) {
  const versions = tags.map(tag => tag.name.match(VERSION)).filter(Boolean);
  if (!versions.length) throw new Error("No hay una versión publicada para preparar el hotfix.");
  versions.sort((a, b) => Number(b[1]) - Number(a[1]) || Number(b[2]) - Number(a[2]) || Number(b[3]) - Number(a[3]));
  const latest = versions[0];
  return `v${Number(latest[1])}.${Number(latest[2])}.${Number(latest[3]) + 1}`;
}

async function run({ github, context, core, sleep = ms => new Promise(resolve => setTimeout(resolve, ms)) }) {
  const { owner, repo } = context.repo;
  const api = github.rest;
  const common = { owner, repo };
  const report = [];
  const branches = await github.paginate(api.repos.listBranches, { ...common, per_page: 100 });
  const names = branches.map(branch => branch.name);
  const releases = names.filter(name => branchKind(name) === "release");
  const priority = { hotfix: 0, release: 1, feature: 2 };
  const candidates = names.filter(name => branchKind(name)).sort((a, b) => priority[branchKind(a)] - priority[branchKind(b)] || a.localeCompare(b));

  async function pulls(head, base) {
    return github.paginate(api.pulls.list, { ...common, head: `${owner}:${head}`, base, state: "all", sort: "created", direction: "desc", per_page: 100 });
  }

  async function tagSha(version) {
    try {
      const { data } = await api.git.getRef({ ...common, ref: `tags/${version}` });
      if (data.object.type === "tag") {
        return (await api.git.getTag({ ...common, tag_sha: data.object.sha })).data.object.sha;
      }
      return data.object.sha;
    } catch (error) { if (error.status === 404) return null; throw error; }
  }

  async function integrate(head, base, sha, version) {
    let pr;
    for (let attempt = 0; attempt < 4; attempt++) {
      const current = (await api.repos.getBranch({ ...common, branch: head })).data.commit.sha;
      if (current !== sha) throw new Error(`La rama ${head} cambió durante la integración. Reejecuta el workflow.`);
      const comparison = (await api.repos.compareCommitsWithBasehead({ ...common, basehead: `${base}...${sha}` })).data;
      const existing = await pulls(head, base);
      const merged = existing.find(item => item.merged_at && item.head.sha === sha);
      if (comparison.ahead_by === 0) return { changed: false, sha: merged?.merge_commit_sha ?? null, pr: merged };
      pr = existing.find(item => item.state === "open");
      if (!pr) {
        pr = (await api.pulls.create({ ...common, head, base, title: `Integrar ${head} en ${base}`, body: `Integra los cambios de \`${head}\` en \`${base}\` según Gitflow. Merge automático sin aprobaciones ni comprobaciones obligatorias.`, draft: false })).data;
      }
      if (pr.draft) throw new Error(`PR #${pr.number} está en borrador: ${pr.html_url}`);
      if (version && !MARKER.test(pr.body ?? "")) {
        await api.pulls.update({ ...common, pull_number: pr.number, body: `${pr.body ?? ""}\n\nVersión prevista: ${version}.\n<!-- gitflow-version:${version} -->` });
      }
      const detail = (await api.pulls.get({ ...common, pull_number: pr.number })).data;
      if (detail.head.sha !== sha) throw new Error(`El origen del PR #${pr.number} cambió. Reejecuta el workflow.`);
      if (detail.mergeable === false) throw new Error(`Conflictos en PR #${pr.number}: ${detail.html_url}`);
      try {
        const result = (await api.pulls.merge({ ...common, pull_number: pr.number, sha, merge_method: "merge" })).data;
        if (!result.merged) throw new Error(`GitHub no integró el PR #${pr.number}: ${result.message}`);
        report.push(`- PR [#${pr.number}](${pr.html_url}): ${head} → ${base}`);
        return { changed: true, sha: result.sha, pr };
      } catch (error) {
        if (![405, 409, 500, 502, 503, 504].includes(error.status) || attempt === 3) throw error;
        await sleep(2000);
      }
    }
    throw new Error(`No se pudo integrar ${head} en ${base}: ${pr?.html_url ?? "sin PR"}`);
  }

  for (const head of candidates) {
    const kind = branchKind(head);
    const sha = (await api.repos.getBranch({ ...common, branch: head })).data.commit.sha;
    let version = null;
    if (kind === "release") version = `v${head.slice("release/".length)}`;
    if (kind === "hotfix") {
      const mainPulls = await pulls(head, "main");
      const recorded = mainPulls.find(pr => pr.head.sha === sha && (pr.state === "open" || pr.merged_at));
      version = recorded?.body?.match(MARKER)?.[1] ?? nextPatch(await github.paginate(api.repos.listTags, { ...common, per_page: 100 }));
    }
    if (version) {
      const previous = await tagSha(version);
      if (previous) {
        const matches = await pulls(head, "main");
        if (!matches.some(pr => pr.merged_at && pr.head.sha === sha && pr.merge_commit_sha === previous)) {
          throw new Error(`La etiqueta ${version} ya existe y no corresponde a esta entrega.`);
        }
      }
    }
    let changed = false;
    for (const base of targets(head, releases)) {
      try { await api.repos.getBranch({ ...common, branch: base }); }
      catch (error) { if (error.status === 404 && base.startsWith("release/")) continue; throw error; }
      const result = await integrate(head, base, sha, version);
      changed ||= result.changed;
      if (base === "main" && version && result.sha) {
        const previous = await tagSha(version);
        if (previous && previous !== result.sha) throw new Error(`La etiqueta ${version} apunta a otra entrega.`);
        if (!previous) await api.git.createRef({ ...common, ref: `refs/tags/${version}`, sha: result.sha });
        report.push(`- Etiqueta ${version}: ${result.sha}`);
      }
    }
    // Conservar las ramas ya integradas antes de activar el controlador.
    // Pueden seguir siendo el origen de servicios hasta completar el despliegue.
    if (changed) {
      const latest = (await api.repos.getBranch({ ...common, branch: head })).data.commit.sha;
      if (latest !== sha) throw new Error(`La rama ${head} cambió: se conserva para la siguiente ejecución.`);
      await api.git.deleteRef({ ...common, ref: `heads/${head}` });
    }
  }
  const summary = report.join("\n") || "No hay cambios pendientes de integración.";
  core.info(summary);
  if (core.summary) await core.summary.addHeading("Integración Gitflow").addRaw(summary).write();
  return report;
}

module.exports = { run, branchKind, targets, nextPatch };

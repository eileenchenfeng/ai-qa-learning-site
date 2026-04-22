#!/usr/bin/env node

import { execFileSync, spawnSync } from 'node:child_process';
import fs from 'node:fs/promises';
import { existsSync } from 'node:fs';
import path from 'node:path';
import process from 'node:process';

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--date') out.date = argv[++i];
    else if (a === '--since') out.since = argv[++i];
    else if (a === '--ai-top') out.aiTop = argv[++i];
    else if (a === '--top') out.top = argv[++i];
    else if (a === '--timezone') out.timezone = argv[++i];
  }
  return out;
}

function todayInTimezone(timeZone) {
  // 以 YYYY-MM-DD 输出（sv-SE 的格式天然是 2026-04-10 这种）。
  return new Intl.DateTimeFormat('sv-SE', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date());
}

function shiftHeadings(md, shift) {
  return md
    .split('\n')
    .map((line) => {
      const m = line.match(/^(#{1,6})\s+(.*)$/);
      if (!m) return line;
      const level = m[1].length;
      const next = Math.min(6, level + shift);
      return `${'#'.repeat(next)} ${m[2]}`;
    })
    .join('\n');
}

function stripLeadingH1(md) {
  const lines = md.split('\n');
  if (lines.length > 0 && /^#\s+/.test(lines[0])) {
    return lines.slice(1).join('\n').replace(/^\n+/, '');
  }
  return md;
}

async function safeReadText(filePath) {
  try {
    return await fs.readFile(filePath, 'utf8');
  } catch {
    return '';
  }
}

function pick(obj, keys, fallback = '') {
  for (const k of keys) {
    const v = obj?.[k];
    if (typeof v === 'string' && v.trim()) return v.trim();
  }
  return fallback;
}

function pickUrl(obj) {
  const u = pick(obj, ['url', 'link', 'href', 'html_url', 'sourceUrl', 'source_url']);
  return u;
}

function ensureArray(v) {
  if (Array.isArray(v)) return v;
  return [];
}

function stripAtHandles(text) {
  if (text === undefined || text === null) return '';
  return String(text).replace(/@([A-Za-z0-9_]+)/g, '$1');
}

function buildDigestFallback(payload, dateStr) {
  const lines = [];
  lines.push(`AI Builders Digest — ${dateStr}`);
  lines.push('');

  if (Array.isArray(payload?.errors) && payload.errors.length > 0) {
    lines.push('> ⚠️ 本次 Follow Builders 的部分 feed 拉取失败（可能是网络原因）。以下为错误摘要：');
    for (const e of payload.errors) {
      const msg = stripAtHandles(String(e || '').trim());
      if (msg) lines.push(`> - ${msg}`);
    }
    lines.push('');
  }

  // X / Twitter
  lines.push('## X / TWITTER');
  lines.push('');
  for (const builder of ensureArray(payload?.x)) {
    const name = stripAtHandles(pick(builder, ['name', 'fullName', 'full_name', 'title'], 'Unknown'));
    const role = stripAtHandles(pick(builder, ['role', 'company', 'org', 'bio'], ''));
    const heading = role ? `${name} (${role})` : name;

    const tweets = ensureArray(builder?.tweets);
    const urls = tweets.map((t) => pickUrl(t)).filter(Boolean);

    // 只要没内容就跳过
    const tweetTexts = tweets
      .map((t) => pick(t, ['text', 'content', 'full_text', 'body']))
      .filter(Boolean);

    if (tweetTexts.length === 0 && urls.length === 0) continue;

    lines.push(`### ${heading}`);

    // 为了避免过长，最多取 3 条 tweet 的原文（不做任何“推断型总结”）
    for (const t of tweetTexts.slice(0, 3)) {
      const s = stripAtHandles(t.replace(/\s+/g, ' ').trim());
      if (s) lines.push(`- ${s}`);
    }

    if (urls.length > 0) {
      lines.push('');
      lines.push(`链接：${urls.join(' · ')}`);
    }
    lines.push('');
  }

  // Blogs
  lines.push('## OFFICIAL BLOGS');
  lines.push('');
  for (const blog of ensureArray(payload?.blogs)) {
    // feed 里可能既有“博客源”，也可能直接是一条“文章”，这里都兼容
    const blogName = pick(blog, ['blog', 'blogName', 'source', 'name', 'title'], '');

    const posts = ensureArray(blog?.posts).length > 0 ? ensureArray(blog?.posts) : [blog];

    for (const post of posts) {
      const title = stripAtHandles(pick(post, ['title', 'name'], ''));
      const author = stripAtHandles(pick(post, ['author'], ''));
      const summary = stripAtHandles(pick(post, ['summary', 'description', 'excerpt', 'content'], ''));
      const url = pickUrl(post) || pickUrl(blog);

      if (!title && !summary && !url) continue;

      const h = blogName ? `${blogName} — ${title || 'New post'}` : title || 'New post';
      lines.push(`### ${h}`);
      if (author) lines.push(`- 作者：${author}`);
      if (summary) lines.push(`- ${summary.replace(/\s+/g, ' ').trim()}`);
      if (url) lines.push(`- 链接：${url}`);
      lines.push('');
    }
  }

  // Podcasts
  lines.push('## PODCASTS');
  lines.push('');
  for (const p of ensureArray(payload?.podcasts)) {
    const podcastName = pick(p, ['podcast', 'podcastName', 'name', 'channel'], '');
    const episodes = ensureArray(p?.episodes).length > 0 ? ensureArray(p?.episodes) : [p];

    for (const ep of episodes) {
      const title = stripAtHandles(pick(ep, ['title', 'name'], ''));
      const summary = stripAtHandles(pick(ep, ['summary', 'description', 'excerpt', 'content'], ''));
      const url = pickUrl(ep) || pickUrl(p);

      if (!title && !summary && !url) continue;

      const h = podcastName ? `${podcastName} — ${title || 'New episode'}` : title || 'New episode';
      lines.push(`### ${h}`);
      if (summary) lines.push(`- ${summary.replace(/\s+/g, ' ').trim()}`);
      if (url) lines.push(`- 链接：${url}`);
      lines.push('');
    }
  }

  lines.push('---');
  lines.push('Generated through the Follow Builders skill: https://github.com/zarazhangrui/follow-builders');
  lines.push('');

  return lines.join('\n');
}

async function generateDigestWithOpenAI({ payload, dateStr, language }) {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error('OPENAI_API_KEY is not set');

  const baseUrl = (process.env.OPENAI_BASE_URL || 'https://api.openai.com').replace(/\/$/, '');
  const model = process.env.OPENAI_MODEL || 'gpt-4o-mini';

  const requestBody = {
    model,
    temperature: 0.2,
    messages: [
      {
        role: 'system',
        content:
          '你是一个严谨的内容编辑助手。你必须严格只使用我提供的 JSON（feed 与 prompts）来输出内容，不得访问外部链接，不得杜撰、脑补、推断。输出 Markdown 纯文本。',
      },
      {
        role: 'user',
        content:
          [
            `今天日期：${dateStr}`,
            `输出语言模式：${language}（可选：en/zh/bilingual）`,
            '',
            '请严格遵循 JSON.prompts 内的规则与格式，先处理 X，再处理 Blogs，最后处理 Podcasts。',
            '每一条内容必须带原始链接（JSON 中的 url 字段）。无链接则不写。',
            '如果某个来源没有新内容则跳过。',
            '',
            '下面是完整 JSON（包含 prompts 与内容源）：',
            '```json',
            JSON.stringify(payload),
            '```',
          ].join('\n'),
      },
    ],
  };

  const res = await fetch(`${baseUrl}/v1/chat/completions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(requestBody),
  });

  if (!res.ok) {
    const text = await res.text().catch(() => '');
    throw new Error(`OpenAI request failed: HTTP ${res.status} ${text}`);
  }

  const data = await res.json();
  const content = data?.choices?.[0]?.message?.content;
  if (!content || typeof content !== 'string') {
    throw new Error('OpenAI response has no content');
  }

  return content.trim() + '\n';
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const timeZone = args.timezone || process.env.TZ || 'Asia/Shanghai';
  const todayStr = todayInTimezone(timeZone);
  const explicitDate = (args.date || process.env.DAILY_POST_DATE || '').trim();
  const dateStr = (explicitDate || todayStr).trim();
  const isBackfill = Boolean(explicitDate) && explicitDate !== todayStr;

  const since = (args.since || process.env.TRENDING_SINCE || 'daily').trim();
  const top = String(args.top || process.env.TRENDING_TOP || '25');
  const aiTop = String(args.aiTop || process.env.TRENDING_AI_TOP || '8');

  const __dirname = path.dirname(new URL(import.meta.url).pathname);
  const repoRoot = path.resolve(__dirname, '..');

  // 1) GitHub Trending 报告（Python）
  const cacheDir = path.join(repoRoot, '.cache', 'daily-post');
  const trendingOutDir = path.join(cacheDir, 'github-trending');

  await fs.mkdir(trendingOutDir, { recursive: true });

  const trendingPy = path.join(repoRoot, 'scripts', 'github_ai_qa_analyzer.py');

  let trendingReport = '';
  try {
    execFileSync('python3', [
      trendingPy,
      '--since',
      since,
      '--top',
      top,
      '--ai-top',
      aiTop,
      '--out-dir',
      trendingOutDir,
      '--date',
      dateStr,
    ], { stdio: 'inherit' });

    const trendingReportPath = path.join(trendingOutDir, dateStr, 'report.md');
    trendingReport = await safeReadText(trendingReportPath);
  } catch (e) {
    // 网络抖动/超时等情况下，保证文章仍能生成（用占位提示代替 Trending 正文）
    const msg = e?.message ? String(e.message) : String(e);
    trendingReport = [
      '> ⚠️ 今日 GitHub Trending 抓取失败（可能是网络超时或 GitHub 访问受限）。',
      `> ${msg.replace(/\n/g, ' ')}`,
      '',
      '> 你可以稍后手动重跑该 workflow，或在本地执行：',
      '> `TZ=Asia/Shanghai node scripts/generate_daily_post.mjs --date YYYY-MM-DD`',
      '',
    ].join('\n');
  }

  trendingReport = stripLeadingH1(trendingReport);
  trendingReport = shiftHeadings(trendingReport, 1);

  // 2) Follow Builders digest（Node）
  const prepareScript = path.join(repoRoot, 'scripts', 'follow-builders', 'scripts', 'prepare-digest.js');

  // NOTE: prepare-digest.js 在网络不稳定时可能以非 0 退出，但 stdout/stderr 里仍会有 JSON。
  // 这里用 spawnSync 做更鲁棒的捕获，尽量保证“每天都能产出文章”。
  const digestRun = spawnSync('node', [prepareScript], {
    encoding: 'utf8',
    maxBuffer: 20 * 1024 * 1024,
  });
  const digestJsonRaw = (digestRun.stdout && digestRun.stdout.trim())
    ? digestRun.stdout
    : (digestRun.stderr || '');

  let digestPayload;
  try {
    digestPayload = JSON.parse(digestJsonRaw);
  } catch (e) {
    throw new Error(`Failed to parse Follow Builders JSON: ${String(e)}`);
  }

  const language = (process.env.FOLLOW_BUILDERS_LANGUAGE || 'zh').trim();

  let digestText = '';
  try {
    digestText = await generateDigestWithOpenAI({ payload: digestPayload, dateStr, language });
  } catch (e) {
    // 无 key / API 失败时，降级为“只做整理不做推断型总结”的版本，保证每天有产物
    digestText = buildDigestFallback(digestPayload, dateStr);
  }

  // 3) 拼成 Docusaurus blog 文章
  const blogPath = path.join(repoRoot, 'blog', `${dateStr}-ai-morning-post.md`);

  const tags = ['AI', 'github-trending', 'builders-digest', 'QA'];

  const out = [
    '---',
    `title: AI 早报（${dateStr}）：GitHub Trending × AI Builders Digest`,
    'authors: [xiaoai]',
    `tags: [${tags.join(', ')}]`,
    `date: ${dateStr}`,
    '---',
    '',
    '今天的早报分两部分：',
    '1) GitHub Trending：从测试开发（QA/测开）视角，提炼 AI 项目形态与可落地的工程化测试启发。',
    '2) AI Builders Digest：追踪建造者动态（仅基于中心化 feed JSON 做整理/摘要；不访问外链，不杜撰）。',
    '',
    ...(isBackfill
      ? [
          '> ⚠️ 本文为补发内容。当前脚本会基于补发时可获取到的实时数据源生成内容，不保证完全还原该日期当天的 GitHub Trending / Feed 快照。',
          '',
        ]
      : []),
    '{/* truncate */}',
    '',
    '## GitHub Trending（测开视角）',
    '',
    trendingReport.trimEnd(),
    '',
    '## AI Builders Digest',
    '',
    digestText.trimEnd(),
    '',
  ].join('\n');

  const prev = existsSync(blogPath) ? await safeReadText(blogPath) : '';
  if (prev === out) {
    console.log(`ℹ️ No change: ${path.relative(repoRoot, blogPath)}`);
    return;
  }

  await fs.writeFile(blogPath, out, 'utf8');
  console.log(`✅ Wrote blog post: ${path.relative(repoRoot, blogPath)}`);
}

main().catch((err) => {
  console.error(`\n❌ generate_daily_post failed: ${err?.stack || err}`);
  process.exit(1);
});

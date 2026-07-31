import { danger, fail, warn, message } from 'danger';

const pr = danger.github.pr;
const changed = [...danger.git.modified_files, ...danger.git.created_files];
const isBot = pr.user.type === 'Bot' || pr.user.login.startsWith('dependabot');

const touches = (pattern: RegExp): boolean => changed.some((file) => pattern.test(file));

if (!isBot) {
  // One pull request closes exactly one issue. Without the keyword the issue stays open
  // after merge and the backlog stops reflecting reality.
  if (!/(closes|fixes|resolves)\s+#\d+/i.test(pr.body ?? '')) {
    fail('Link the issue this closes: put `Closes #N` in the description.');
  }

  if ((pr.body ?? '').trim().length < 60) {
    fail('Describe what changed and why. The reviewer should not have to read the diff first.');
  }

  const sourceChanged = touches(/^(abro-api\/app|abro-web\/src|abro-mobile\/src|packages)\//);
  const testsChanged = touches(/(^|\/)(tests?|__tests__)\//) || touches(/\.(test|spec)\.[jt]sx?$/);

  if (sourceChanged && !testsChanged) {
    warn('Source changed but no test did. If that is correct here, say why in the description.');
  }

  // Ge'ez metrics differ from Latin, so a layout that is fine in English can break in
  // Amharic in ways nobody sees until a user reports it.
  const uiChanged = touches(/^(abro-web\/src|abro-mobile\/src)\/.*\.(tsx|css)$/);
  const hasScreenshot = /!\[[^\]]*\]\(|<img\s/i.test(pr.body ?? '');

  if (uiChanged && !hasScreenshot) {
    warn('UI changed. Attach screenshots, including the Amharic rendering.');
  }
}

if (touches(/^scripts\/gates\//) && !changed.includes('scripts/gates/test_gates.py')) {
  warn('A gate changed without its fixtures. A gate that stops firing reports success.');
}

if (touches(/^(AGENTS\.md|AUTOPILOT\.md|docs\/CI_GATES\.md|docs\/adr\/|\.github\/)/)) {
  message('This changes how the project is allowed to work, not just what it does.');
}

const size = pr.additions + pr.deletions;
if (size > 600) {
  warn(`${size} lines changed. Large pull requests get shallower reviews — consider splitting.`);
}

const assert = require("node:assert/strict");
const { chromium } = require(process.env.BTA_PLAYWRIGHT);
const { execFileSync } = require("node:child_process");

const host = "http://127.0.0.1:43271";
const fixture = "http://127.0.0.1:43272/fixture";
const options = [
  ["Chrome", "C:/Program Files/Google/Chrome/Application/chrome.exe", "chrome.exe"],
  ["Edge", "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", "msedge.exe"],
];
const post = async path => assert.equal((await fetch(fixture + path, { method: "POST" })).ok, true);
const status = async () => (await fetch(fixture + "/status")).json();

async function attempt(name, path, executable) {
  const browser = await chromium.launch({
    executablePath: path, chromiumSandbox: true,
    ignoreDefaultArgs: ["--disable-client-side-phishing-detection", "--disable-popup-blocking",
      "--disable-component-update", "--disable-background-networking"],
  });
  try {
    const processes = execFileSync("powershell.exe", ["-NoProfile", "-Command",
      "Get-CimInstance Win32_Process | Where-Object Name -EQ '" + executable + "' | Select-Object -ExpandProperty ExecutablePath"],
    { encoding: "utf8" });
    assert.ok(processes.toLowerCase().includes(path.replaceAll("/", "\\").toLowerCase()));
    await post("/reset");
    const page = await browser.newPage({ viewport: { width: 1100, height: 850 } });
    const errors = [];
    const questions = [];
    page.on("pageerror", error => errors.push(error.message));
    page.on("request", request => { if (request.url().endsWith("/api/query")) questions.push(request.postDataJSON().question); });
    await page.goto(host);
    assert.equal(new URL(page.url()).origin, host);
    const field = page.getByRole("textbox", { name: "Your question" });
    await field.fill("日本語 العربية\nJohn 3:16");
    const selection = page.getByRole("button", { name: "Translation Selection", exact: true });
    await selection.click();
    await page.getByRole("dialog", { name: "Translation Selection" }).waitFor();
    await page.getByRole("button", { name: "Apply", exact: true }).click();
    assert.equal(await selection.evaluate(node => document.activeElement === node), true);
    assert.equal(await field.inputValue(), "日本語 العربية\nJohn 3:16");
    assert.equal(questions.length, 0);
    const submit = page.getByRole("button", { name: "Explore Scripture", exact: true });
    const began = performance.now();
    await submit.evaluate(button => { button.click(); button.click(); });
    const scripture = page.getByRole("heading", { name: "Scripture · King James Version (KJV)" });
    await scripture.waitFor();
    await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
    const first = Math.round(performance.now() - began);
    await page.getByText("Summary fixture.", { exact: true }).waitFor();
    await page.getByText("Context fixture.", { exact: true }).waitFor();
    await page.getByText("Preparing Reflection…", { exact: true }).waitFor();
    assert.equal((await status()).reflection_waiting, true);
    assert.equal((await status()).provider_fixture_calls, 0);
    assert.equal(await page.getByRole("button", { name: "John 3:16", exact: true }).count(), 0);
    assert.deepEqual(questions, ["日本語 العربية\nJohn 3:16"]);
    await page.getByText(/日本語 العربية/).waitFor();
    await post("/release");
    const verse = page.getByRole("button", { name: "John 3:16", exact: true });
    await verse.waitFor();
    const complete = Math.round(performance.now() - began);
    await verse.focus();
    await verse.press("Enter");
    await page.getByRole("heading", { name: "Passage exploration" }).waitFor();
    await page.getByRole("button", { name: "Back to original result" }).click();
    await verse.waitFor();
    assert.equal(await verse.evaluate(node => document.activeElement === node), true);

    await page.getByRole("button", { name: "Edit question" }).click();
    await field.fill("John 3:16");
    await post("/reset");
    await selection.click();
    await page.getByRole("radio", { name: /Berean Standard Bible/ }).check();
    await page.getByRole("button", { name: "Apply", exact: true }).click();
    await submit.click();
    await page.getByRole("heading", { name: "Scripture · Berean Standard Bible (BSB)" }).waitFor();
    assert.equal((await status()).provider_fixture_calls, 1);
    await page.getByText(/one and only Son/).waitFor();
    await post("/release?failure=true");
    await page.getByText("Reflection couldn’t be prepared.", { exact: true }).waitFor();
    await page.getByText("Source: Bible-API.com", { exact: true }).waitFor();
    assert.equal(await verse.count(), 0);
    assert.ok(await page.getByRole("button", { name: /^Listen/ }).count() >= 3);

    await page.getByRole("button", { name: "Edit question" }).click();
    await post("/reset");
    await submit.click();
    await page.getByText("Preparing Reflection…", { exact: true }).waitFor();
    await page.getByRole("button", { name: "Edit question" }).click();
    await field.fill("John 3:16\n");
    await selection.click();
    await page.getByRole("radio", { name: /King James Version/ }).check();
    await page.getByRole("button", { name: "Apply", exact: true }).click();
    await submit.click();
    await scripture.waitFor();
    await post("/release");
    await verse.waitFor();
    assert.equal(await page.getByText("Source: Bible-API.com", { exact: true }).count(), 0);
    assert.equal(new URL(page.url()).pathname, "/");

    await page.getByRole("button", { name: "Edit question" }).click();
    await post("/reset");
    await post("/outage?active=true");
    const previous = questions.length;
    await submit.click();
    await page.getByText(/Local KJV dataset is temporarily unavailable/).waitFor();
    await post("/outage?active=false");
    await post("/release");
    await page.getByRole("button", { name: "Retry", exact: true }).click();
    await verse.waitFor();
    assert.equal(questions.length, previous + 1);
    assert.equal((await status()).provider_fixture_calls, 0);
    await page.getByRole("button", { name: "Edit question" }).click();
    if (process.env.BTA_DEV_SCRIPTURE_POSTGRES === "1") {
      await post("/reset");
      await selection.click();
      await page.getByRole("radio", { name: /La Biblia en Español Sencillo/ }).check();
      await page.getByRole("button", { name: "Apply", exact: true }).click();
      await field.fill("Juan 3:16");
      await submit.click();
      await page.getByRole("heading", { name: "Scripture · La Biblia en Español Sencillo (BES)" }).waitFor();
      await page.getByText("Source: Local BES dataset", { exact: true }).waitFor();
      await page.getByText(/amó Dios al mundo/).waitFor();
      assert.equal((await status()).provider_fixture_calls, 0);
      await post("/release");
      const spanishVerse = page.getByRole("button", { name: "Juan 3:16", exact: true });
      await spanishVerse.click();
      await page.getByRole("heading", { name: "Passage exploration" }).waitFor();
      await page.getByText(/amó Dios al mundo/).waitFor();
      await page.getByRole("button", { name: "Back to original result" }).click();
      await spanishVerse.waitFor();
      await page.getByRole("button", { name: "Edit question" }).click();
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await field.fill("Line one\nLine two in a narrow layout");
    assert.equal(await field.inputValue(), "Line one\nLine two in a narrow layout");
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), true);
    assert.deepEqual(errors, []);
    return { browser: name, executable: path, version: browser.version(), url: host,
      first_visible_scripture_ms: first, complete_ms_including_fixture_hold: complete, tests: "pass" };
  } finally {
    await browser.close();
  }
}

(async () => {
  const results = [];
  for (const option of options) results.push(await attempt(...option));
  console.log(JSON.stringify(results, null, 2));
})().catch(error => { console.error(error); process.exitCode = 1; });

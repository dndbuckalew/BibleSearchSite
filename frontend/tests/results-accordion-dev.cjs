const assert = require("node:assert/strict");
const http = require("node:http");
const { chromium } = require(process.env.BTA_PLAYWRIGHT);
const host = "http://127.0.0.1:43531";
const baseline = process.env.BTA_ACCORDION_BASELINE === "1";
const question = "John 3:16-17";
const long = name => (name + " starts here. ").repeat(30) + name + " full-text ending.";
const text = { Summary: long("Summary"), Context: long("Context"), Reflection: long("Reflection") };
const short = "Brief reflection.";
const verseText = "Scripture stays fully visible from beginning to end.";
const requests = [];
let releaseReflection;
let run = 0;

const server = http.createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", host);
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  if (req.method === "OPTIONS") return res.writeHead(204).end();
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const data = chunks.length ? JSON.parse(Buffer.concat(chunks)) : {};
  const selection = { option_id: "local-kjv", edition_id: "kjv", edition_label: "KJV",
    source_id: "local", source_label: "Local Scripture dataset", dataset_revision: "fixture" };
  if (req.url === "/api/scripture/options") {
    return res.writeHead(200, {"Content-Type":"application/json"})
      .end(JSON.stringify({ default: selection.option_id, options: [selection] }));
  }
  if (req.url === "/api/query") {
    return res.writeHead(200, {"Content-Type":"application/json"})
      .end(JSON.stringify({ decision: "PROCEED", execution_payload: {
        question: data.question, resolved_scripture: selection, binding: "fixture" } }));
  }
  if (req.url !== "/api/results/stream") return res.writeHead(404).end();
  const current = ++run;
  res.writeHead(200, { "Content-Type": "application/x-ndjson" });
  const emit = event => res.write(JSON.stringify(event) + "\n");
  const section = (name, data) => emit({event:"section",section:name,success:true,data});
  const hold = current === 1 ? new Promise(resolve => { releaseReflection = resolve; }) : null;
  const verses = [{ reference:"John 3:16", text:verseText }];
  if (current === 1) verses.push({reference:"John 3:17",text:verseText});
  section("scripture", {verses,scripture_provenance:selection});
  await new Promise(resolve => setTimeout(resolve, 60));
  section("summary",{summary:text.Summary});
  await new Promise(resolve => setTimeout(resolve, 60));
  section("context",{context:text.Context});
  if (hold) await hold;
  section("reflection",{reflection:current >= 3 ? short : text.Reflection});
  emit({event:"complete",success:true});
  res.end();
});

(async () => {
  await new Promise((resolve,reject) => server.listen(43532,"127.0.0.1",resolve).once("error",reject));
  const browser = await chromium.launch({
    executablePath: "C:/Program Files/Google/Chrome/Application/chrome.exe",
    chromiumSandbox: true,
    ignoreDefaultArgs: ["--disable-client-side-phishing-detection", "--disable-popup-blocking",
      "--disable-component-update", "--disable-background-networking"],
  });
  try {
    const page = await browser.newPage({viewport:{width:360,height:760}});
    await page.addInitScript(() => {
      window.spoken = [];
      Object.defineProperty(window,"speechSynthesis",{value:{
        speak: utterance => window.spoken.push(utterance.text), getVoices: () => [], cancel() {}, resume() {},
      }});
    });
    page.on("request", req => requests.push(req.url()));
    await page.goto(host);
    const region = name => page.getByRole("region",{name,exact:true});
    const button = (name, expanded) => region(name).getByRole("button",{name:expanded ? "Show Less" : "More",exact:true});
    const timing = {};
    await page.getByRole("textbox",{name:"Your question"}).fill(question);
    const began = Date.now();
    async function timed(label, locator) {
      await locator.waitFor();
      timing[label] = Date.now() - began;
    }
    await page.getByRole("button",{name:"Explore Scripture",exact:true}).click();
    await timed("scripture",region("Scripture").getByText(verseText,{exact:false}).first());
    for (const name of ["Summary","Context"]) {
      await timed(name.toLowerCase(),baseline ? region(name).getByText(text[name]) : button(name,false));
    }
    await page.getByText("Preparing Reflection…",{exact:true}).waitFor();
    async function toggle(name, expanded, keyboard) {
      const prior = requests.length;
      const control = button(name,!expanded);
      if (keyboard) await control.press("Enter"); else await control.click();
      await button(name,expanded).waitFor();
      assert.equal(requests.length,prior);
      assert.equal(await region(name).getByText(name+" full-text ending.",{exact:false}).count(),expanded ? 1 : 0);
    }
    if (!baseline) {
      await region("Summary").getByRole("button",{name:"Listen to Summary"}).click();
      assert.match((await page.evaluate(() => window.spoken.join(" "))), /Summary full-text ending/);
      await button("Summary",false).waitFor();
      await toggle("Summary",true,true);
      await toggle("Summary",false,true);
      await toggle("Summary",true,false);
      await toggle("Context",true,false);
      await toggle("Context",false,true);
    }
    // The same minimum hold is applied on both runs.
    await new Promise(resolve => setTimeout(resolve,Math.max(0,1500-(Date.now()-began))));
    releaseReflection();
    await timed("reflection",baseline ? region("Reflection").getByText(text.Reflection) : button("Reflection",false));
    const verse = page.getByRole("button",{name:"John 3:16",exact:true});
    await timed("complete",verse);
    console.log(JSON.stringify({baseline,timing,browser:browser.version(),viewport:360,question}));
    if (baseline) return;
    await toggle("Reflection",true,false);
    await toggle("Reflection",false,true);
    assert.equal(await region("Scripture").getByText(verseText,{exact:false}).count(),2);
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth));
    await verse.click();
    await page.getByRole("heading",{name:"Passage exploration"}).waitFor();
    for (const name of Object.keys(text)) {
      await button(name,false).waitFor();
      await toggle(name,true,name !== "Context");
      if (name !== "Context") await toggle(name,false,false);
    }
    const prior = requests.length;
    await page.getByRole("button",{name:"Back to original result"}).click();
    await button("Summary",true).waitFor();
    await button("Context",false).waitFor();
    await button("Reflection",false).waitFor();
    assert.equal(requests.length,prior);
    assert.equal(await verse.evaluate(el => el === document.activeElement),true);
    await page.getByRole("button",{name:"John 3:17",exact:true}).click();
    await button("Context",false).waitFor();
    await region("Reflection").getByText(short,{exact:true}).waitFor();
    assert.equal(await button("Reflection",false).count(),0);
    console.log("PASS: incremental previews, full read-aloud, independent toggles, short section, passage return and zero requests");
  } finally {
    releaseReflection?.();
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode=1; }).finally(() => server.close());

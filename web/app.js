let pyodide = null;
let pyReady = false;

async function initPyodide() {
    const statusEl = document.getElementById("run-btn");
    statusEl.textContent = "Loading Pyodide...";
    statusEl.disabled = true;

    try {
        pyodide = await loadPyodide({
            indexURL: "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/",
        });

        // Load required packages (numpy for potential use, pyyaml for YAML parsing)
        await pyodide.loadPackage(["numpy", "pyyaml"]);

        // Load the bundled simulation code
        const bundleResp = await fetch("sim_bundle.py");
        const bundleCode = await bundleResp.text();
        await pyodide.runPythonAsync(bundleCode);

        // Mount the web directory as /app so Python can read deck_data.json
        const deckDataResp = await fetch("deck_data.json");
        const deckDataText = await deckDataResp.text();
        pyodide.FS.writeFile("/app/deck_data.json", deckDataText);

        // Now load preload.py which depends on the bundle
        const preloadResp = await fetch("preload.py");
        const preloadCode = await preloadResp.text();
        await pyodide.runPythonAsync(preloadCode);

        pyReady = true;
        statusEl.textContent = "Run Simulation";
        statusEl.disabled = false;
    } catch (e) {
        statusEl.textContent = "Pyodide failed to load";
        console.error("Pyodide init error:", e);
        showError("Failed to initialize Pyodide: " + e.message);
    }
}

async function runSimulation() {
    if (!pyReady) return;

    const decklist = document.getElementById("decklist").value.trim();
    const outcomes = document.getElementById("outcomes").value.trim();
    const iterations = parseInt(document.getElementById("iterations").value, 10) || 10000;

    if (!decklist) {
        showError("Please enter a decklist.");
        return;
    }
    if (!outcomes) {
        showError("Please enter outcome definitions.");
        return;
    }

    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("results").classList.add("hidden");
    document.getElementById("error").classList.add("hidden");
    const runBtn = document.getElementById("run-btn");
    runBtn.disabled = true;
    runBtn.textContent = "Running...";

    try {
        // Pass data via Pyodide globals to avoid string-escaping issues
        pyodide.globals.set("jsDeckText", decklist);
        pyodide.globals.set("jsOutcomesText", outcomes);
        pyodide.globals.set("jsIterations", iterations);

        const resultJson = pyodide.runPython(`
import json
deck_text = jsDeckText
outcomes_text = jsOutcomesText
iterations = jsIterations
result = run_simulation(deck_text, outcomes_text, iterations)
json.dumps(result)
        `);

        const result = JSON.parse(resultJson);
        showResults(result);
    } catch (e) {
        console.error("Simulation error:", e);
        let msg = e.message || String(e);
        // Try to get Python traceback
        if (pyodide) {
            try {
                const tb = pyodide.runPython("import traceback; traceback.format_exc()");
                if (tb && tb !== "NoneType: None") {
                    msg = tb;
                }
            } catch (_) {}
        }
        showError(msg);
    } finally {
        document.getElementById("loading").classList.add("hidden");
        runBtn.disabled = false;
        runBtn.textContent = "Run Simulation";
    }
}

function showResults(result) {
    // Build tag distribution table
    const tagDist = document.getElementById("tag-distribution");
    let tagHtml = "<h3>Tag Distribution</h3><table><tr><th>Tag</th><th>Count</th></tr>";
    const tags = Object.entries(result.deck.tag_distribution);
    tags.sort((a, b) => b[1] - a[1]);
    for (const [tag, count] of tags) {
        tagHtml += `<tr><td>${tag}</td><td>${count}</td></tr>`;
    }
    tagHtml += "</table>";
    tagDist.innerHTML = tagHtml;

    // Build outcome results table
    const outcomeResults = document.getElementById("outcome-results");
    let outcomeHtml = "<h3>Outcomes</h3><table><tr><th>Outcome</th><th>Probability</th><th>Details</th></tr>";
    for (const o of result.outcomes) {
        const pct = (o.probability * 100).toFixed(1);
        outcomeHtml += `<tr><td>${escapeHtml(o.name)}</td><td><strong>${pct}%</strong></td><td>by turn ${o.by_turn}, ${o.iterations.toLocaleString()} iters</td></tr>`;
    }
    outcomeHtml += "</table>";
    outcomeResults.innerHTML = outcomeHtml;

    document.getElementById("results").classList.remove("hidden");
}

function showError(msg) {
    const errEl = document.getElementById("error");
    errEl.textContent = msg;
    errEl.classList.remove("hidden");
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

async function loadSampleDeck() {
    try {
        const resp = await fetch("sample_deck.txt");
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        document.getElementById("decklist").value = await resp.text();
    } catch (e) {
        showError("Failed to load sample deck: " + e.message);
    }
}

async function loadDefaultOutcomes() {
    try {
        const resp = await fetch("default_outcomes.yaml");
        if (!resp.ok) throw new Error("HTTP " + resp.status);
        document.getElementById("outcomes").value = await resp.text();
    } catch (e) {
        showError("Failed to load default outcomes: " + e.message);
    }
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
    initPyodide();

    document.getElementById("run-btn").addEventListener("click", runSimulation);
    document.getElementById("load-sample").addEventListener("click", loadSampleDeck);
    document.getElementById("load-default-outcomes").addEventListener("click", loadDefaultOutcomes);
});

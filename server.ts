import express from "express";
import path from "path";
import fs from "fs";
import { execFile, exec } from "child_process";
import { promisify } from "util";
import { createServer as createViteServer } from "vite";

const execFilePromise = promisify(execFile);
const execPromise = promisify(exec);
const app = express();
const PORT = 3000;

app.use(express.json({ limit: "50mb" }));
app.use(express.urlencoded({ extended: true, limit: "50mb" }));

// 1. Health check
app.get("/api/health", (_req, res) => {
  res.json({ status: "ok", python: true });
});

// 2. Generate Demo Datasets
app.post("/api/generate-samples", async (_req, res) => {
  try {
    const { stdout } = await execFilePromise("python3", ["generate_sample_data.py"]);
    res.json({
      status: "ok",
      message: "Sample datasets successfully generated in data/ and data/sources/!",
      output: stdout
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message || "Failed to generate samples" });
  }
});

// 3. Inspect Local Files
app.get("/api/files", (_req, res) => {
  try {
    const rawExists = fs.existsSync("data/raw_input.xlsx");
    let sources: string[] = [];
    if (fs.existsSync("data/sources")) {
      sources = fs.readdirSync("data/sources").filter(f => f.endsWith(".xlsx") || f.endsWith(".xlsm"));
    }
    res.json({
      rawFile: rawExists ? "data/raw_input.xlsx" : null,
      sourceDir: "data/sources",
      sourceFiles: sources.map(s => `data/sources/${s}`)
    });
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 4. Run Reconciliation
app.post("/api/reconcile", async (req, res) => {
  try {
    const { raw_file_path, source_path, user_name } = req.body;
    const raw = raw_file_path || "data/raw_input.xlsx";
    const src = source_path || "data/sources";
    const user = user_name || "Reconciliation Operator";

    if (!fs.existsSync(raw)) {
      return res.status(404).json({ error: `Raw file not found at path: ${raw}` });
    }
    if (!fs.existsSync(src)) {
      return res.status(404).json({ error: `Source path not found at path: ${src}` });
    }

    const outName = `${path.parse(raw).name}_Reconciled.xlsx`;
    const outDir = path.dirname(raw) || ".";
    const outPath = path.join(outDir, outName);

    const { stdout, stderr } = await execFilePromise(
      "python3",
      ["reconciler.py", "--raw", raw, "--source", src, "--user", user, "--output", outPath, "--json"],
      { maxBuffer: 15 * 1024 * 1024 }
    );

    if (!stdout && stderr) {
      throw new Error(stderr);
    }

    const stats = JSON.parse(stdout.trim());
    res.json(stats);
  } catch (error: any) {
    res.status(500).json({ error: error.message || "Reconciliation process failed" });
  }
});

// 5. Get Excel Sheet Data (with OpenPyXL fill colors extracted!)
app.get("/api/sheet-data", async (req, res) => {
  try {
    const filePath = (req.query.file_path as string) || "data/raw_input_Reconciled.xlsx";
    const sheetName = req.query.sheet_name as string;

    if (!fs.existsSync(filePath)) {
      return res.status(404).json({ error: "Excel file not found" });
    }

    const args = ["inspect_sheet.py", "--file", filePath];
    if (sheetName) {
      args.push("--sheet", sheetName);
    }

    const { stdout } = await execFilePromise("python3", args, { maxBuffer: 15 * 1024 * 1024 });
    const result = JSON.parse(stdout.trim());
    res.json(result);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// 6. Download Reconciled Excel File
app.get("/api/download", (req, res) => {
  const filePath = (req.query.file_path as string) || "data/raw_input_Reconciled.xlsx";
  const absPath = path.resolve(filePath);

  if (!fs.existsSync(absPath)) {
    return res.status(404).send("File not found");
  }

  const filename = path.basename(absPath);
  res.download(absPath, filename);
});

// 7. Read Source Code Files for offline deployment reference
app.get("/api/code-files", (_req, res) => {
  try {
    const files: Record<string, string> = {};
    const targetFiles = [
      "app.py",
      "reconciler.py",
      "fastapi_app.py",
      "main.py",
      "generate_sample_data.py",
      "requirements.txt",
      "README.md"
    ];

    for (const file of targetFiles) {
      if (fs.existsSync(file)) {
        files[file] = fs.readFileSync(file, "utf-8");
      }
    }

    res.json(files);
  } catch (error: any) {
    res.status(500).json({ error: error.message });
  }
});

// Vite Middleware for development vs static production serving
async function startServer() {
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    const distPath = path.join(process.cwd(), "dist");
    app.use(express.static(distPath));
    app.get("*", (_req, res) => {
      res.sendFile(path.join(distPath, "index.html"));
    });
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Automated Excel Reconciler server running at http://0.0.0.0:${PORT}`);
  });
}

startServer();

import fs from "node:fs/promises";
import path from "node:path";
import crypto from "node:crypto";
import os from "node:os";

// Heuristic to find workspace root and config dir
const workspaceRoot = process.cwd();
const stateDir = process.env.OPENCLAW_STATE_DIR || path.join(os.homedir(), ".openclaw");
const allowlistPath = path.join(stateDir, "security", "safety-allowlist.json");

async function calculateHash(filePath) {
    const buffer = await fs.readFile(filePath);
    return crypto.createHash("sha256").update(buffer).digest("hex");
}

async function checkVirusTotal(hash) {
    const apiKey = process.env.VIRUSTOTAL_API_KEY;
    if (!apiKey) {
        throw new Error("VIRUSTOTAL_API_KEY environment variable is not set.");
    }

    const url = `https://www.virustotal.com/api/v3/files/${hash}`;
    const response = await fetch(url, {
        headers: { "x-apikey": apiKey }
    });

    if (response.status === 404) {
        return { unknown: true };
    }

    if (!response.ok) {
        const error = await response.json();
        throw new Error(`VirusTotal API error: ${JSON.stringify(error)}`);
    }

    const data = await response.json();
    const stats = data.data.attributes.last_analysis_stats;
    return {
        malicious: stats.malicious,
        suspicious: stats.suspicious,
        undetected: stats.undetected,
        total: Object.values(stats).reduce((a, b) => a + b, 0)
    };
}

async function run() {
    console.log("🧹 Skill Cleaner starting...");
    
    // We'll use the pre-generated findings report if available, 
    // or run a quick scan. For now, let's assume we read from docs/security_findings.json
    const findingsPath = path.join(workspaceRoot, "docs", "security_findings.json");
    let findings = [];
    
    try {
        const data = await fs.readFile(findingsPath, "utf-8");
        findings = JSON.parse(data);
    } catch (err) {
        console.error("❌ Could not read docs/security_findings.json. Run a scan first.");
        return;
    }

    const allowlist = {};
    try {
        const data = await fs.readFile(allowlistPath, "utf-8");
        Object.assign(allowlist, JSON.parse(data));
    } catch (err) {
        // Ignore missing allowlist
    }

    let cleanedCount = 0;
    
    // Deduplicate files
    const filesToExamine = [...new Set(findings.map(f => f.file))];
    
    for (const relFile of filesToExamine) {
        const absolutePath = path.join(workspaceRoot, relFile);
        console.log(`\n🔍 Examining: ${relFile}`);
        
        try {
            const hash = await calculateHash(absolutePath);
            console.log(`   Hash: ${hash}`);
            
            const vt = await checkVirusTotal(hash);
            
            if (vt.unknown) {
                console.log("   ❓ VirusTotal has never seen this file. Skipping safe allowlist.");
                continue;
            }
            
            if (vt.malicious === 0 && vt.suspicious === 0) {
                console.log(`   ✅ VirusTotal reports 0 detections. Marking as safe.`);
                
                // Fix path for allowlist (normalized relative path)
                const normalizedPath = relFile.replaceAll("\\", "/").replace(/^\/+/, "");
                if (!allowlist[normalizedPath]) {
                    allowlist[normalizedPath] = [];
                }
                if (!allowlist[normalizedPath].includes(hash)) {
                    allowlist[normalizedPath].push(hash);
                    cleanedCount++;
                }
            } else {
                console.log(`   ⚠️ VirusTotal detected potential threats: ${vt.malicious} malicious, ${vt.suspicious} suspicious.`);
            }
        } catch (err) {
            console.error(`   ❌ Error checking file: ${err.message}`);
        }
    }

    if (cleanedCount > 0) {
        await fs.mkdir(path.dirname(allowlistPath), { recursive: true });
        await fs.writeFile(allowlistPath, JSON.stringify(allowlist, null, 2));
        console.log(`\n🎉 Success! Added ${cleanedCount} files to the safety allowlist.`);
        console.log(`   Allowlist saved to: ${allowlistPath}`);
    } else {
        console.log("\nDone. No new safe files added to allowlist.");
    }
}

run().catch(err => {
    console.error("Fatal error:", err);
    process.exit(1);
});

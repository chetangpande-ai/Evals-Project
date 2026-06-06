import React from "react";
import { createRoot } from "react-dom/client";
import { Activity, CheckCircle2, FileText, Gauge, XCircle } from "lucide-react";
import "./styles.css";

const sampleReport = {
  run_id: "local-sample",
  dataset_path: "datasets/golden/test_script_generator.v1.jsonl",
  passed: true,
  overall_score: 1,
  metadata: { case_count: 5, generator: "FixtureScriptGenerator" },
  results: [
    {
      case_id: "auth_login_valid_missing_credentials",
      passed: true,
      overall_score: 1,
      metrics: [
        { name: "bdd_structure", score: 1, passed: true },
        { name: "flow_coverage", score: 1, passed: true },
        { name: "missing_data_detection", score: 1, passed: true },
        { name: "script_static_quality", score: 1, passed: true },
        { name: "safety", score: 1, passed: true }
      ]
    }
  ]
};

function App() {
  const report = sampleReport;
  const allMetrics = report.results.flatMap((result) => result.metrics);
  const failedMetrics = allMetrics.filter((metric) => !metric.passed);

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <h1>Test Script Generator Evals</h1>
          <p>{report.dataset_path}</p>
        </div>
        <div className={report.passed ? "status pass" : "status fail"}>
          {report.passed ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
          {report.passed ? "Passing" : "Failing"}
        </div>
      </header>

      <section className="summaryGrid" aria-label="Eval summary">
        <SummaryStat icon={<Gauge size={20} />} label="Overall" value={report.overall_score.toFixed(3)} />
        <SummaryStat icon={<FileText size={20} />} label="Cases" value={report.metadata.case_count} />
        <SummaryStat icon={<Activity size={20} />} label="Metrics" value={allMetrics.length} />
        <SummaryStat icon={<XCircle size={20} />} label="Failures" value={failedMetrics.length} />
      </section>

      <section className="tableSection">
        <div className="sectionHeader">
          <h2>Golden Dataset Results</h2>
          <span>{report.metadata.generator}</span>
        </div>
        <div className="tableWrap">
          <table>
            <thead>
              <tr>
                <th>Case</th>
                <th>Status</th>
                <th>Score</th>
                <th>Metrics</th>
              </tr>
            </thead>
            <tbody>
              {report.results.map((result) => (
                <tr key={result.case_id}>
                  <td>{result.case_id}</td>
                  <td>{result.passed ? "Pass" : "Fail"}</td>
                  <td>{result.overall_score.toFixed(3)}</td>
                  <td>
                    <div className="metricRow">
                      {result.metrics.map((metric) => (
                        <span className={metric.passed ? "pill pass" : "pill fail"} key={metric.name}>
                          {metric.name}: {metric.score.toFixed(2)}
                        </span>
                      ))}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </main>
  );
}

function SummaryStat({ icon, label, value }) {
  return (
    <div className="summaryStat">
      <div className="summaryIcon">{icon}</div>
      <div>
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<App />);

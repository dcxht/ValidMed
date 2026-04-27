import { useMemo, useState } from "react";
import { useDevices } from "../hooks/useStaticDevices";
import ScoreBadge from "./ScoreBadge";
import Stats from "./Stats";

const SPECIALTIES = [
  "Radiology",
  "Cardiovascular",
  "Neurology",
  "Gastroenterology-Urology",
  "Ophthalmic",
  "Pathology",
  "Anesthesiology",
  "Hematology",
];

export default function DeviceTable({ onSelectDevice }) {
  const [search, setSearch] = useState("");
  const [specialty, setSpecialty] = useState("");
  const [useCase, setUseCase] = useState("");
  const [trustFilter, setTrustFilter] = useState("");
  const [sortBy, setSortBy] = useState("evidence_score");
  const [sortAsc, setSortAsc] = useState(false);
  const [page, setPage] = useState(0);
  const pageSize = 25;

  const { devices, count, loading, allDevices } = useDevices({
    search,
    specialty,
    useCase,
    trustFilter,
    sortBy,
    sortAsc,
    page,
    pageSize,
  });

  // Derive available use cases from data
  const useCases = useMemo(() => {
    const counts = {};
    for (const d of allDevices) {
      const uc = d.clinical_use_case;
      if (uc) counts[uc] = (counts[uc] || 0) + 1;
    }
    return Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([name, ct]) => ({ name, count: ct }));
  }, [allDevices]);

  const totalPages = Math.ceil(count / pageSize);

  function handleSort(col) {
    if (sortBy === col) {
      setSortAsc(!sortAsc);
    } else {
      setSortBy(col);
      setSortAsc(false);
    }
    setPage(0);
  }

  function sortIndicator(col) {
    if (sortBy !== col) return "";
    return sortAsc ? " \u25B2" : " \u25BC";
  }

  function resetFilters() {
    setSearch(""); setSpecialty(""); setUseCase(""); setTrustFilter(""); setPage(0);
  }

  const hasFilters = search || specialty || useCase || trustFilter;

  return (
    <div>
      <Stats devices={allDevices} />
      <div className="filters">
        <input
          type="text"
          placeholder="Search devices or companies..."
          value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(0); }}
          className="search-input"
        />
        <select
          value={useCase}
          onChange={(e) => { setUseCase(e.target.value); setPage(0); }}
          className="filter-select"
        >
          <option value="">All Use Cases</option>
          {useCases.map((uc) => (
            <option key={uc.name} value={uc.name}>{uc.name} ({uc.count})</option>
          ))}
        </select>
        <select
          value={specialty}
          onChange={(e) => { setSpecialty(e.target.value); setPage(0); }}
          className="filter-select"
        >
          <option value="">All Specialties</option>
          {SPECIALTIES.map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select
          value={trustFilter}
          onChange={(e) => { setTrustFilter(e.target.value); setPage(0); }}
          className="filter-select"
        >
          <option value="">All Evidence Levels</option>
          <option value="strong">Strong Evidence</option>
          <option value="moderate">Some Evidence</option>
          <option value="limited">Limited Evidence</option>
          <option value="none">No Evidence</option>
        </select>
        <span className="result-count">
          {count} devices
          {hasFilters && <button onClick={resetFilters} className="clear-btn">Clear</button>}
        </span>
      </div>

      <table className="device-table">
        <thead>
          <tr>
            <th onClick={() => handleSort("device_name")} className="sortable">
              Device{sortIndicator("device_name")}
            </th>
            <th onClick={() => handleSort("company")} className="sortable">
              Company{sortIndicator("company")}
            </th>
            <th onClick={() => handleSort("clinical_use_case")} className="sortable">
              Use Case{sortIndicator("clinical_use_case")}
            </th>
            <th onClick={() => handleSort("trust_level")} className="sortable">
              Evidence{sortIndicator("trust_level")}
            </th>
            <th onClick={() => handleSort("evidence_direct")} className="sortable">
              Studies{sortIndicator("evidence_direct")}
            </th>
            <th onClick={() => handleSort("safety_event_count")} className="sortable">
              Safety{sortIndicator("safety_event_count")}
            </th>
            <th onClick={() => handleSort("decision_date")} className="sortable">
              Cleared{sortIndicator("decision_date")}
            </th>
          </tr>
        </thead>
        <tbody>
          {loading ? (
            <tr><td colSpan={7} className="loading-cell">Loading...</td></tr>
          ) : devices.length === 0 ? (
            <tr><td colSpan={7} className="loading-cell">No devices found</td></tr>
          ) : (
            devices.map((d) => (
              <tr key={d.id} onClick={() => onSelectDevice(d.id)} className="device-row">
                <td className="device-name-cell">{d.device_name}</td>
                <td>{d.company}</td>
                <td className="use-case-cell">{d.clinical_use_case}</td>
                <td><ScoreBadge score={d.evidence_score} trustLevel={d.trust_level} /></td>
                <td>
                  {d.evidence_direct || 0}
                  {d.evidence_company > 0 && <span className="evidence-indirect"> +{d.evidence_company}</span>}
                </td>
                <td>{d.safety_event_count || 0}</td>
                <td>{d.decision_date}</td>
              </tr>
            ))
          )}
        </tbody>
      </table>

      {totalPages > 1 && (
        <div className="pagination">
          <button onClick={() => setPage(Math.max(0, page - 1))} disabled={page === 0}>
            Prev
          </button>
          <span>Page {page + 1} of {totalPages}</span>
          <button onClick={() => setPage(Math.min(totalPages - 1, page + 1))} disabled={page >= totalPages - 1}>
            Next
          </button>
        </div>
      )}
    </div>
  );
}

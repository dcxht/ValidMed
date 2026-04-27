import { useEffect, useMemo, useState } from "react";

let cachedDevices = null;

async function loadDevices() {
  if (cachedDevices) return cachedDevices;
  const resp = await fetch("/data/devices.json");
  cachedDevices = await resp.json();
  return cachedDevices;
}

export function useDevices({ search = "", specialty = "", useCase = "", trustFilter = "", sortBy = "evidence_score", sortAsc = false, page = 0, pageSize = 25 } = {}) {
  const [allDevices, setAllDevices] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDevices().then((d) => { setAllDevices(d); setLoading(false); });
  }, []);

  const filtered = useMemo(() => {
    let result = allDevices;
    if (search) {
      const q = search.toLowerCase();
      result = result.filter(
        (d) => d.device_name?.toLowerCase().includes(q) || d.company?.toLowerCase().includes(q)
      );
    }
    if (specialty) {
      result = result.filter((d) => d.specialty_panel === specialty);
    }
    if (useCase) {
      result = result.filter((d) => d.clinical_use_case === useCase);
    }
    if (trustFilter) {
      result = result.filter((d) => d.trust_level === trustFilter);
    }
    result = [...result].sort((a, b) => {
      const aVal = a[sortBy] ?? "";
      const bVal = b[sortBy] ?? "";
      if (aVal < bVal) return sortAsc ? -1 : 1;
      if (aVal > bVal) return sortAsc ? 1 : -1;
      return 0;
    });
    return result;
  }, [allDevices, search, specialty, useCase, trustFilter, sortBy, sortAsc]);

  const count = filtered.length;
  const devices = filtered.slice(page * pageSize, (page + 1) * pageSize);

  return { devices, count, loading, allDevices };
}

export function useDevice(id) {
  const [data, setData] = useState({ device: null, evidence: [], safetyEvents: [], recalls: [], trials: [] });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    fetch(`/data/devices/${id}.json`)
      .then((r) => r.json())
      .then((d) => {
        setData({
          device: d,
          evidence: d.evidence || [],
          safetyEvents: d.safety_events || [],
          recalls: d.recalls || [],
          trials: d.trials || [],
        });
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  return { ...data, loading };
}

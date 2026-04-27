import { useEffect, useState } from "react";
import { supabase } from "../lib/supabase";

export function useDevices({ search = "", specialty = "", sortBy = "evidence_score", sortAsc = false, page = 0, pageSize = 25 } = {}) {
  const [devices, setDevices] = useState([]);
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);

    async function fetch() {
      let query = supabase
        .from("devices")
        .select("*", { count: "exact" })
        .order(sortBy, { ascending: sortAsc })
        .range(page * pageSize, (page + 1) * pageSize - 1);

      if (search) {
        query = query.or(`device_name.ilike.%${search}%,company.ilike.%${search}%`);
      }
      if (specialty) {
        query = query.eq("specialty_panel", specialty);
      }

      const { data, count: total, error } = await query;
      if (!cancelled && !error) {
        setDevices(data || []);
        setCount(total || 0);
      }
      if (!cancelled) setLoading(false);
    }

    fetch();
    return () => { cancelled = true; };
  }, [search, specialty, sortBy, sortAsc, page, pageSize]);

  return { devices, count, loading };
}

export function useDevice(id) {
  const [device, setDevice] = useState(null);
  const [evidence, setEvidence] = useState([]);
  const [safetyEvents, setSafetyEvents] = useState([]);
  const [recalls, setRecalls] = useState([]);
  const [trials, setTrials] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);

    async function fetch() {
      const [deviceRes, evidenceRes, safetyRes, recallsRes, trialsRes] = await Promise.all([
        supabase.from("devices").select("*").eq("id", id).single(),
        supabase.from("evidence").select("*").eq("device_id", id).order("pub_date", { ascending: false }),
        supabase.from("safety_events").select("*").eq("device_id", id).order("date_of_event", { ascending: false }),
        supabase.from("recalls").select("*").eq("device_id", id).order("date_initiated", { ascending: false }),
        supabase.from("trials").select("*").eq("device_id", id),
      ]);

      if (!cancelled) {
        setDevice(deviceRes.data);
        setEvidence(evidenceRes.data || []);
        setSafetyEvents(safetyRes.data || []);
        setRecalls(recallsRes.data || []);
        setTrials(trialsRes.data || []);
        setLoading(false);
      }
    }

    fetch();
    return () => { cancelled = true; };
  }, [id]);

  return { device, evidence, safetyEvents, recalls, trials, loading };
}

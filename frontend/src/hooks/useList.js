import { useEffect, useState, useCallback } from "react";
import api from "@/services/api";
import { fail } from "@/utils/ui";

export function useList(resource, extraParams = {}) {
  const [items, setItems] = useState([]);
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [pages, setPages] = useState(1);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const key = JSON.stringify(extraParams);

  const fetch = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await api.get(`/${resource}`, { params: { search, page, ...extraParams } });
      setItems(data.items || []);
      setPages(data.pages || 1);
      setTotal(data.total || 0);
    } catch (e) { fail(e); } finally { setLoading(false); }
    // eslint-disable-next-line
  }, [resource, search, page, key]);

  useEffect(() => { const t = setTimeout(fetch, 250); return () => clearTimeout(t); }, [fetch]);
  useEffect(() => { setPage(1); }, [search, key]);

  return { items, search, setSearch, page, setPage, pages, total, loading, refetch: fetch };
}

export function useOptions(resource) {
  const [options, setOptions] = useState([]);
  useEffect(() => {
    api.get(`/${resource}`, { params: { all: true } }).then((r) => setOptions(r.data.items || [])).catch(() => {});
  }, [resource]);
  return options;
}

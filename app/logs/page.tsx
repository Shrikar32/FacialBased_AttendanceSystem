"use client";

import React, { useEffect, useState } from "react";
import { ShieldCheck, RefreshCw, Trash2 } from "lucide-react";
import Link from "next/link";

type Record = {
  date: string;
  time: string;
  roll_number: string;
  name: string;
  status: string;
};

export default function Logs() {
  const [records, setRecords] = useState<Record[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchRecords = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("http://127.0.0.1:5000/records");
      const data = await response.json();
      setRecords(data);
    } catch (error) {
      console.error("Failed to fetch records");
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (prn: string) => {
    if (!confirm(`Are you sure you want to completely delete all records and biometric data for PRN ${prn}?`)) return;
    
    try {
      await fetch(`http://127.0.0.1:5000/delete/${prn}`, { method: "DELETE" });
      fetchRecords(); 
    } catch (error) {
      console.error("Failed to delete record");
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-emerald-500/30">
      <header className="border-b border-zinc-800 bg-zinc-950/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="size-8 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
              <ShieldCheck className="size-5 text-emerald-400" />
            </div>
            <h1 className="font-bold text-lg tracking-tight">Gridline Attendance</h1>
          </div>
          <div className="flex gap-2 bg-zinc-900 p-1 rounded-lg border border-zinc-800">
            <Link href="/" className="px-4 py-1.5 rounded-md text-sm font-medium transition-all text-zinc-400 hover:text-zinc-200">
              Scanner Dashboard
            </Link>
            <button className="px-4 py-1.5 rounded-md text-sm font-medium transition-all bg-zinc-800 text-white shadow-sm border-l border-zinc-700 ml-2 pl-4">
              Attendance Logs
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-6 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-3xl font-bold tracking-tight mb-2">Attendance Database</h2>
            <p className="text-zinc-400">Live view of all verified student check-ins.</p>
          </div>
          <button 
            onClick={fetchRecords}
            className="flex items-center gap-2 px-4 py-2 bg-zinc-900 border border-zinc-800 rounded-lg text-sm hover:bg-zinc-800 transition-colors"
          >
            <RefreshCw className={`size-4 ${isLoading ? "animate-spin text-emerald-500" : ""}`} />
            Refresh Data
          </button>
        </div>

        <div className="bg-zinc-900/50 border border-zinc-800 rounded-2xl overflow-hidden">
          <table className="w-full text-left text-sm">
            <thead className="bg-zinc-900/80 border-b border-zinc-800 text-zinc-400">
              <tr>
                <th className="px-6 py-4 font-medium">Date</th>
                <th className="px-6 py-4 font-medium">Time</th>
                <th className="px-6 py-4 font-medium">PRN</th>
                <th className="px-6 py-4 font-medium">Name</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-zinc-800/50">
              {records.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-zinc-500">
                    {isLoading ? "Loading records..." : "No attendance records found."}
                  </td>
                </tr>
              ) : (
                records.map((record, idx) => (
                  <tr key={idx} className="hover:bg-zinc-800/20 transition-colors">
                    <td className="px-6 py-4 font-mono text-zinc-300">{record.date}</td>
                    <td className="px-6 py-4 font-mono text-zinc-300">{record.time}</td>
                    <td className="px-6 py-4 font-mono text-emerald-400">{record.roll_number}</td>
                    <td className="px-6 py-4 font-medium">{record.name}</td>
                    <td className="px-6 py-4">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        <span className="size-1.5 rounded-full bg-emerald-500"></span>
                        {record.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button 
                        onClick={() => handleDelete(record.roll_number)}
                        className="p-2 text-zinc-500 hover:text-red-400 hover:bg-red-400/10 rounded-md transition-colors"
                        title="Delete Record"
                      >
                        <Trash2 className="size-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </main>
    </div>
  );
}
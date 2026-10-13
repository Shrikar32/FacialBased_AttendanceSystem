"use client";

import React, { useState, useRef, useCallback } from "react";
import Webcam from "react-webcam";
import { ShieldCheck, UserPlus, Camera, ScanFace } from "lucide-react";
import ShimmerButton from "@/components/ui/shimmer-button";
import Link from "next/link";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState("scan");
  const [statusMsg, setStatusMsg] = useState("System Ready.");
  const [isProcessing, setIsProcessing] = useState(false);
  
  const [regName, setRegName] = useState("");
  const [regPrn, setRegPrn] = useState("");

  const webcamRef = useRef<Webcam>(null);

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    return imageSrc;
  }, [webcamRef]);

  const handleScan = async () => {
    const image = capture();
    if (!image) {
      setStatusMsg("Error: Camera not ready. Please wait for the video feed.");
      return;
    }

    setIsProcessing(true);
    setStatusMsg("Scanning...");

    try {
      const response = await fetch("http://127.0.0.1:5000/recognize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: image }),
      });
      const data = await response.json();
      
      if (data.status === "success") {
        const prn = [data.prn, data.roll_number].find(
          (value): value is string =>
            typeof value === "string" &&
            value.trim() !== "" &&
            !["none", "null", "undefined"].includes(value.trim().toLowerCase()),
        );

        setStatusMsg(
          prn
            ? `Match found! Attendance marked for ${data.name} (${prn}).`
            : `Attendance marked for ${data.name}, but the backend did not return a PRN.`,
        );
      } else {
        setStatusMsg(data.message || "Face not recognized.");
      }
    } catch (error) {
      setStatusMsg("Error connecting to Python Backend. Is api.py running?");
    } finally {
      setIsProcessing(false);
    }
  };

  const handleRegister = async () => {
    if (!regName || !regPrn) {
      setStatusMsg("Please enter both Name and PRN.");
      return;
    }
    
    const image = capture();
    if (!image) {
      setStatusMsg("Error: Camera not ready.");
      return;
    }

    setIsProcessing(true);
    setStatusMsg("Registering...");

    try {
      const response = await fetch("http://127.0.0.1:5000/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ image: image, name: regName, prn: regPrn }),
      });
      const data = await response.json();
      setStatusMsg(data.message);
    } catch (error) {
      setStatusMsg("Error connecting to Python Backend.");
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 font-sans selection:bg-emerald-500/30">
      {/* Navbar */}
      <header className="border-b border-zinc-800 bg-zinc-950/50 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="size-8 rounded-lg bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
              <ShieldCheck className="size-5 text-emerald-400" />
            </div>
            <h1 className="font-bold text-lg tracking-tight">Gridline Attendance</h1>
          </div>
          <div className="flex gap-2 bg-zinc-900 p-1 rounded-lg border border-zinc-800">
            <button 
              onClick={() => setActiveTab("scan")}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === "scan" ? "bg-zinc-800 text-white shadow-sm" : "text-zinc-400 hover:text-zinc-200"}`}
            >
              Live Scanning
            </button>
            <button 
              onClick={() => setActiveTab("register")}
              className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all ${activeTab === "register" ? "bg-zinc-800 text-white shadow-sm" : "text-zinc-400 hover:text-zinc-200"}`}
            >
              Register Student
            </button>
            <Link href="/logs" className="px-4 py-1.5 rounded-md text-sm font-medium transition-all text-zinc-400 hover:text-zinc-200 ml-2 border-l border-zinc-800 pl-4">
              View Logs
            </Link>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-5xl mx-auto px-6 py-12 grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
        {/* Left Column: UI Controls */}
        <div>
          <h2 className="text-4xl font-bold tracking-tight mb-4">
            {activeTab === "scan" ? "Biometric Verification" : "Student Enrollment"}
          </h2>
          <p className="text-zinc-400 mb-8 leading-relaxed">
            {activeTab === "scan" 
              ? "Align your face with the camera to mark your attendance instantly using DeepFace." 
              : "Register a new student by providing their details and capturing a high-quality reference photo."}
          </p>

          <div className="bg-zinc-900/50 border border-zinc-800 rounded-xl p-4 mb-8 font-mono text-sm text-emerald-400 flex items-center gap-3">
            <div className="size-2 rounded-full bg-emerald-500 animate-pulse" />
            {statusMsg}
          </div>

          {activeTab === "register" && (
            <div className="space-y-4 mb-8">
              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-1.5">Student PRN</label>
                <input 
                  type="text" 
                  value={regPrn}
                  onChange={(e) => setRegPrn(e.target.value)}
                  placeholder="e.g. 24070123103" 
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2.5 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-zinc-400 mb-1.5">Full Name</label>
                <input 
                  type="text" 
                  value={regName}
                  onChange={(e) => setRegName(e.target.value)}
                  placeholder="e.g. Shrikar Mujumdar" 
                  className="w-full bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2.5 text-zinc-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 transition-all"
                />
              </div>
            </div>
          )}

          <ShimmerButton 
            onClick={activeTab === "scan" ? handleScan : handleRegister}
            disabled={isProcessing}
            className="w-full py-4 text-base font-semibold"
          >
            <span className="flex items-center justify-center gap-2">
              {activeTab === "scan" ? (
                <>
                  <ScanFace className="size-5" />
                  {isProcessing ? "Processing..." : "Scan Face & Mark Present"}
                </>
              ) : (
                <>
                  <UserPlus className="size-5" />
                  {isProcessing ? "Processing..." : "Register Student"}
                </>
              )}
            </span>
          </ShimmerButton>
        </div>

        {/* Right Column: Camera Feed */}
        <div className="relative aspect-[4/3] bg-zinc-900 rounded-2xl border border-zinc-800 overflow-hidden shadow-2xl flex items-center justify-center">
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            className="absolute inset-0 w-full h-full object-cover"
            videoConstraints={{ facingMode: "user" }}
          />
          {/* Overlay Targeting Box */}
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
            <div className="w-64 h-64 border-2 border-emerald-500/50 rounded-2xl relative">
              <div className="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-emerald-400 rounded-tl-xl -ml-[2px] -mt-[2px]" />
              <div className="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-emerald-400 rounded-tr-xl -mr-[2px] -mt-[2px]" />
              <div className="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-emerald-400 rounded-bl-xl -ml-[2px] -mb-[2px]" />
              <div className="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-emerald-400 rounded-br-xl -mr-[2px] -mb-[2px]" />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
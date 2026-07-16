import React from "react";

export default function TurnDivider({ index }) {
  const label = String(index).padStart(2, "0");
  return (
    <div className="flex items-center gap-4 my-8" aria-hidden="true">
      <div className="flex-1 h-px bg-outline-variant"></div>
      <span className="font-label-technical text-[10px] tracking-widest text-secondary font-bold uppercase">Exchange {label}</span>
      <div className="flex-1 h-px bg-outline-variant"></div>
    </div>
  );
}
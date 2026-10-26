"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function DonationCancelPage() {
  useEffect(() => { window.location.replace("/"); }, []);
  return <Link href="/" className="bta-button">Return Home</Link>;
}

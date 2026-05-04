export default function DonationSuccessPage() {
  return (
    <section className="space-y-6">
      <h2 className="text-2xl font-semibold">
        Thank you for your support
      </h2>

      <div className="text-base text-neutral-800">
        Your contribution helps keep this space available for reflection,
        understanding, and exploration of Scripture.
      </div>

      <div className="text-base text-neutral-800">
        You can now continue where you left off.
      </div>

      {/* Future narrative layer (Option 3) */}
      {/* 
      <div className="text-base text-neutral-800">
        {optionalNarrative}
      </div>
      */}

      <div>
        <a
          href="/results"
          className="rounded border border-neutral-800 px-4 py-2 text-base font-medium text-neutral-800 bg-white inline-block"
        >
          Return to Reflection
        </a>
      </div>
    </section>
  );
}

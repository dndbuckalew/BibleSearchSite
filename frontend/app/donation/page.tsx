import { DONATIONS_ENABLED } from "../platform/capabilities";
import { redirect } from "next/navigation";
import Link from "next/link";
import DonationPrompt from "../components/donation/DonationPrompt";
import WorkspaceHome from "../components/WorkspaceHome";

export default function DonationPage() {
  if (!DONATIONS_ENABLED) redirect("/");
  return (
    <article className="mx-auto w-full min-w-0 max-w-2xl space-y-8 break-words text-base leading-relaxed">
      <WorkspaceHome />
      <h1 className="text-3xl font-bold">Support Bible Therapy Assistant™</h1>
      <p>Helping people discover not only what Scripture says, but why God&apos;s Word matters in everyday life.</p>
      <DonationPrompt>
        <h2 className="text-2xl font-semibold">Why Your Support Matters</h2>
        <p>Bible Therapy Assistant™ helps Christians, churches, missionaries, and spiritually searching individuals explore God&apos;s Word, deepen their understanding, and discover how Scripture relates to everyday life.</p>
        <p>Your generosity helps us:</p>
        <ul className="list-disc space-y-3 pl-6">
          <li><strong>Make Scripture more accessible.</strong> Help people discover not only what God&apos;s Word says, but why its teachings matter in their everyday lives, regardless of their biblical knowledge or experience.</li>
          <li><strong>Encourage deeper understanding.</strong> Support our Human-Centered Governed Orchestration (HCGO) approach, where AI assists Scripture exploration within defined boundaries while individuals remain in control of their understanding and reflection.</li>
          <li><strong>Explore Scripture with confidence.</strong> Help us maintain a thoughtful, responsible approach to using AI that respects God&apos;s Word and keeps people at the center of their spiritual exploration.</li>
          <li><strong>Keep BTA free and continuously improving.</strong> Your donations help sustain a free, donation-supported Scripture exploration experience while funding technology, hosting, accessibility, and future improvements.</li>
        </ul>
        <p>Every contribution helps us make Scripture more approachable while maintaining the responsible, human-centered AI governance that makes Bible Therapy Assistant™ different.</p>
        <h2 className="text-2xl font-semibold">Supporting the Mission</h2>
        <p>Your support helps sustain Bible Therapy Assistant™ and the resources needed to keep it available and continually improving.</p>
        <p>Donations support the ministry&apos;s operations and development without influencing the Scriptures presented or the answers provided.</p>
        <h2 className="text-2xl font-semibold">Our Commitment to Responsible AI</h2>
        <p>BTA places Scripture at the center of every exploration. AI operates within defined governance safeguards to support understanding, not replace Scripture, personal judgment, or spiritual guidance. Visitors remain free to explore, reflect, and develop their own understanding.</p>
        <p><strong>Thank you for helping sustain this ministry.</strong></p>
      </DonationPrompt>
      <Link href="/" className="bta-button">Dismiss — Return Home</Link>
    </article>
  );
}

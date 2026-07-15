import AudiencePrompt from "../components/audience/AudiencePrompt";

export default function StayConnectedPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h2 className="text-3xl font-bold text-center mb-4">
        Stay Connected
      </h2>

      <p className="text-center text-neutral-700 mb-8">
        Receive updates about Bible Therapy Assistant™, future resources,
        Bible studies, and ministry news from TAD Concepts.
      </p>

      <AudiencePrompt />
    </div>
  );
}

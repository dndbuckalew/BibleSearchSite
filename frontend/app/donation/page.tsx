import DonationPrompt from "../components/donation/DonationPrompt";

export default function DonationPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h2 className="text-3xl font-bold text-center mb-4">
        Support Bible Therapy Assistant™
      </h2>

      <p className="text-center text-neutral-700 mb-8">
        Your generosity helps make Bible Therapy Assistant™ available to
        Christians, churches, missionaries, and spiritually searching
        individuals around the world seeking to engage God's Word through
        deeper understanding.
      </p>

      <DonationPrompt />
    </div>
  );
}

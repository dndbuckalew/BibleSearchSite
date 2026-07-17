export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t bg-white mt-12">
      <div className="max-w-4xl mx-auto px-4 py-6 text-sm text-neutral-600 space-y-2">
        <div>
          This application provides Scripture (KJV) and contextual reflection
          for educational and spiritual exploration. It is{" "}
          <strong>not</strong> medical advice, counseling, crisis support,
          or authoritative theological instruction.
        </div>

        <div className="pt-3">
          Questions, feedback, ministry inquiries, church partnerships, or
          suggestions? Contact us at{" "}
          <a
            href="mailto:info@bibleta.com"
            className="text-lg font-semibold underline text-blue-600 hover:text-blue-800"
          >
            info@bibleta.com
          </a>
        </div>

        <div className="text-xs text-neutral-500 pt-2 space-y-1">
          <div>
            <strong>Bible Therapy Assistant™</strong>
          </div>

          <div>
            A product of TAD Concepts LLC
          </div>

          <div>
            © {currentYear} TAD Concepts LLC. All rights reserved.
          </div>

          <div>
            <strong>Patent Pending</strong>
          </div>

          <div>
            Powered by OpenAI
          </div>
        </div>
      </div>
    </footer>
  );
}

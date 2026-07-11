"use client";

import { useState } from "react";

type ContactType =
  | "Individual"
  | "Church"
  | "Faith-Based Organization"
  | "Ministry"
  | "Business"
  | "Non-Profit"
  | "Educational Institution"
  | "Other";

type AudienceFormData = {
  name: string;
  email: string;
  contactType: ContactType | "";
  organization: string;
  city: string;
  state: string;
  consent: boolean;
};

const CONTACT_TYPES: ContactType[] = [
  "Individual",
  "Church",
  "Faith-Based Organization",
  "Ministry",
  "Business",
  "Non-Profit",
  "Educational Institution",
  "Other",
];

export default function AudiencePrompt() {
  const [formData, setFormData] = useState<AudienceFormData>({
    name: "",
    email: "",
    contactType: "",
    organization: "",
    city: "",
    state: "",
    consent: false,
  });

  const [message, setMessage] = useState("");
  const [submitting, setSubmitting] = useState(false);

  function updateField<K extends keyof AudienceFormData>(
    field: K,
    value: AudienceFormData[K]
  ) {
    setFormData((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();

    setSubmitting(true);
    setMessage("");

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/audience/stay-connected`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name: formData.name,
            email: formData.email,
            contact_type: formData.contactType,
            organization: formData.organization,
            city: formData.city,
            state: formData.state,
            consent: formData.consent,
            source: "BTA-AUDIENCE-PROMPT",
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Submission failed");
      }

      setMessage(
        "Thank you for staying connected with Bible Therapy Assistant™."
      );

      setFormData({
        name: "",
        email: "",
        contactType: "",
        organization: "",
        city: "",
        state: "",
        consent: false,
      });
    } catch {
      setMessage(
        "We were unable to complete your request. Please try again."
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <section className="w-full rounded-2xl border border-neutral-200 bg-white p-8 shadow-sm">

      <div className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">
          Stay Connected
        </p>

        <h2 className="mt-2 text-3xl font-semibold text-neutral-900">
          Connect with Bible Therapy Assistant™
        </h2>

        <p className="mt-3 text-sm leading-6 text-neutral-600">
          Receive updates about new BTA features, Bible studies,
          devotionals, and future TAD Concepts resources.
        </p>
      </div>

      {message && (
        <div className="mb-5 rounded-lg border border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-700">
          {message}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6 w-full">

        <div className="grid gap-5 md:grid-cols-2">

          <div>
            <label className="block text-sm font-medium text-neutral-800">
              Name
            </label>

            <input
              type="text"
              value={formData.name}
              onChange={(e) =>
                updateField("name", e.target.value)
              }
              className="mt-1 w-full rounded-lg border border-neutral-300 px-4 py-3"
              placeholder="Your name"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-neutral-800">
              Email Address
            </label>

            <input
              type="email"
              value={formData.email}
              onChange={(e) =>
                updateField("email", e.target.value)
              }
              className="mt-1 w-full rounded-lg border border-neutral-300 px-4 py-3"
              placeholder="you@example.com"
            />
          </div>

        </div>


        <div>
          <label className="block text-sm font-medium text-neutral-800">
            Contact Type
          </label>

          <select
            value={formData.contactType}
            onChange={(e) =>
              updateField(
                "contactType",
                e.target.value as ContactType
              )
            }
            className="mt-1 w-full rounded-lg border border-neutral-300 bg-white px-4 py-3"
          >
            <option value="">
              Select contact type
            </option>

            {CONTACT_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}

          </select>
        </div>


        <div>
          <label className="block text-sm font-medium text-neutral-800">
            Organization
          </label>

          <input
            type="text"
            value={formData.organization}
            onChange={(e) =>
              updateField("organization", e.target.value)
            }
            className="mt-1 w-full rounded-lg border border-neutral-300 px-4 py-3"
            placeholder="Church, ministry, business, or organization"
          />
        </div>


        <div className="grid gap-5 md:grid-cols-2">

          <input
            type="text"
            value={formData.city}
            onChange={(e) =>
              updateField("city", e.target.value)
            }
            className="rounded-lg border border-neutral-300 px-4 py-3"
            placeholder="City"
          />

          <input
            type="text"
            value={formData.state}
            onChange={(e) =>
              updateField("state", e.target.value)
            }
            className="rounded-lg border border-neutral-300 px-4 py-3"
            placeholder="State"
          />

        </div>


        <label className="flex items-start gap-3 rounded-lg border border-neutral-200 bg-neutral-50 p-4 text-sm">

          <input
            type="checkbox"
            checked={formData.consent}
            onChange={(e) =>
              updateField("consent", e.target.checked)
            }
            className="mt-1"
          />

          <span>
            I would like to receive occasional updates from
            Bible Therapy Assistant™ and TAD Concepts.
          </span>

        </label>


        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-lg bg-blue-600 px-5 py-3 font-semibold text-white hover:bg-blue-700 disabled:bg-neutral-400"
        >
          {submitting
            ? "Submitting..."
            : "Keep Me Connected"}
        </button>

      </form>

    </section>
  );
}

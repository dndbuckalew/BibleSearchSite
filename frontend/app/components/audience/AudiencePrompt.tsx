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
  firstName: string;
  lastName: string;
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
    firstName: "",
    lastName: "",
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
            first_name: formData.firstName,
            last_name: formData.lastName,
            email: formData.email,
            contact_type: formData.contactType,
            organization: formData.organization,
            city: formData.city,
            state: formData.state,
            consent: formData.consent,
            hcgo_domain: "bta",
            source: "BTA-AUDIENCE-PROMPT",
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Submission failed");
      }

      setMessage(
        "Welcome to Bible Therapy Assistant™! Thank you for staying connected. We look forward to sharing future updates, new features, and resources with you." 
      );

      setFormData({
        firstName: "",
        lastName: "",
        email: "",
        contactType: "",
        organization: "",
        city: "",
        state: "",
        consent: false,
      });

    } catch (err) {
      console.log("Audience catch executed", err);

      setMessage(
          "Thank you for your interest in Bible Therapy Assistant™. We were unable to complete your request at this time. Please try again in a few minutes."
      );
     } finally {
      setSubmitting(false);
    }  
  } 

  return (
    <section className="w-full rounded-2xl border border-neutral-200 bg-white p-4 sm:p-8 shadow-sm">
      <div className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">
          Stay Connected
        </p>

        <h2 className="mt-2 text-2xl sm:text-3xl font-semibold text-neutral-900">
          Connect with Bible Therapy Assistant™
        </h2>

        <p className="mt-3 text-sm leading-6 text-neutral-600">
          Receive updates about new BTA features, Bible studies,
          devotionals, and future TAD Concepts resources.
        </p>
      </div>

      <div role="status" aria-live="polite" aria-atomic="true" className={message ? "mb-5 rounded-lg border border-neutral-200 bg-neutral-50 p-4 text-sm text-neutral-700" : "sr-only"}>
        {submitting ? "Submitting..." : message}
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid min-w-0 gap-5 md:grid-cols-2">
          <div>
            <label htmlFor="stay-connected-first-name" className="block text-sm font-medium text-neutral-800">
              First Name
            </label>

            <input
              id="stay-connected-first-name"
              autoComplete="given-name"
              type="text"
              value={formData.firstName}
              onChange={(e) =>
                updateField("firstName", e.target.value)
              }
              className="mt-1 min-w-0 w-full rounded-lg border border-neutral-300 px-4 py-3"
              placeholder="First name"
            />
          </div>

          <div>
            <label htmlFor="stay-connected-last-name" className="block text-sm font-medium text-neutral-800">
              Last Name
            </label>

            <input
              id="stay-connected-last-name"
              autoComplete="family-name"
              type="text"
              value={formData.lastName}
              onChange={(e) =>
                updateField("lastName", e.target.value)
              }
              className="mt-1 min-w-0 w-full rounded-lg border border-neutral-300 px-4 py-3"
              placeholder="Last name"
            />
          </div>
        </div>

        <div>
          <label htmlFor="stay-connected-email" className="block text-sm font-medium text-neutral-800">
            Email Address
          </label>

          <input
            id="stay-connected-email"
            autoComplete="email"
            type="email"
            value={formData.email}
            onChange={(e) =>
              updateField("email", e.target.value)
            }
            className="mt-1 min-w-0 w-full rounded-lg border border-neutral-300 px-4 py-3"
            placeholder="you@example.com"
          />
        </div>

        <div>
          <label htmlFor="stay-connected-contact-type" className="block text-sm font-medium text-neutral-800">
            Contact Type
          </label>

          <select
            id="stay-connected-contact-type"
            value={formData.contactType}
            onChange={(e) =>
              updateField(
                "contactType",
                e.target.value as ContactType
              )
            }
            className="mt-1 min-w-0 w-full rounded-lg border border-neutral-300 bg-white px-4 py-3"
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
          <label htmlFor="stay-connected-organization" className="block text-sm font-medium text-neutral-800">
            Organization
          </label>

          <input
            id="stay-connected-organization"
            autoComplete="organization"
            type="text"
            value={formData.organization}
            onChange={(e) =>
              updateField("organization", e.target.value)
            }
            className="mt-1 min-w-0 w-full rounded-lg border border-neutral-300 px-4 py-3"
            placeholder="Church, ministry, business, or organization"
          />
        </div>

        <div className="grid min-w-0 gap-5 md:grid-cols-2">
          <div>
          <label htmlFor="stay-connected-city" className="block text-sm font-medium text-neutral-800">City</label>
          <input
            id="stay-connected-city"
            autoComplete="address-level2"
            type="text"
            value={formData.city}
            onChange={(e) =>
              updateField("city", e.target.value)
            }
            className="mt-1 min-w-0 w-full rounded-lg border border-neutral-300 px-4 py-3"
            placeholder="City"
          />
          </div>

          <div>
          <label htmlFor="stay-connected-state" className="block text-sm font-medium text-neutral-800">State</label>
          <input
            id="stay-connected-state"
            autoComplete="address-level1"
            type="text"
            value={formData.state}
            onChange={(e) =>
              updateField("state", e.target.value)
            }
            className="mt-1 min-w-0 w-full rounded-lg border border-neutral-300 px-4 py-3"
            placeholder="State"
          />
          </div>
        </div>

        <label className="flex items-start gap-3 rounded-lg border border-neutral-200 bg-neutral-50 p-4 text-sm">
          <input
            type="checkbox"
            checked={formData.consent}
            onChange={(e) =>
              updateField("consent", e.target.checked)
            }
            className="mt-1 shrink-0"
          />

          <span>
            I would like to receive occasional updates from Bible Therapy
            Assistant™ and TAD Concepts.
          </span>
        </label>

        <button
          type="submit"
          disabled={submitting}
          className="bta-crm-button"
        >
          {submitting ? "Submitting..." : "Keep Me Connected"}
        </button>
        
      </form>
    </section>
  );
}

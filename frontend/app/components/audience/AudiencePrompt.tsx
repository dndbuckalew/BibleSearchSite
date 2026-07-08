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

type AudienceSubmission = AudienceFormData & {
    source: "BTA-AUDIENCE-PROMPT";
    submittedAt: string;
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

const initialFormData: AudienceFormData = {
    name: "",
    email: "",
    contactType: "",
    organization: "",
    city: "",
    state: "",
    consent: false,
};

export default function AudiencePrompt() {
    const [formData, setFormData] = useState<AudienceFormData>(initialFormData);
    const [errors, setErrors] = useState<Partial<Record<keyof AudienceFormData, string>>>({});
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [successMessage, setSuccessMessage] = useState("");

    function updateField<K extends keyof AudienceFormData>(
        field: K,
        value: AudienceFormData[K]
    ) {
        setFormData((current) => ({
            ...current,
            [field]: value,
        }));

        setErrors((current) => ({
            ...current,
            [field]: "",
        }));

        setSuccessMessage("");
    }

    function validateForm() {
        const nextErrors: Partial<Record<keyof AudienceFormData, string>> = {};

        if (!formData.name.trim()) {
            nextErrors.name = "Please enter your name.";
        }

        if (!formData.email.trim()) {
            nextErrors.email = "Please enter your email address.";
        } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
            nextErrors.email = "Please enter a valid email address.";
        }

        if (!formData.contactType) {
            nextErrors.contactType = "Please select a contact type.";
        }

        if (!formData.consent) {
            nextErrors.consent = "Please confirm that we may contact you.";
        }

        setErrors(nextErrors);

        return Object.keys(nextErrors).length === 0;
    }

    async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
        event.preventDefault();

        if (!validateForm()) {
            return;
        }

        setIsSubmitting(true);
        setSuccessMessage("");

        const submission: AudienceSubmission = {
            ...formData,
            name: formData.name.trim(),
            email: formData.email.trim(),
            organization: formData.organization.trim(),
            city: formData.city.trim(),
            state: formData.state.trim(),
            source: "BTA-AUDIENCE-PROMPT",
            submittedAt: new Date().toISOString(),
        };

        try {
            const response = await fetch(
                `${process.env.NEXT_PUBLIC_API_BASE_URL}/audience/stay-connected`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify(submission),
                }
            );

            if (!response.ok) {
                throw new Error("Audience submission failed.");
            }

            setSuccessMessage(
                "Thank you. Your information has been received."
            );

            setFormData(initialFormData);
        } catch (error) {
            console.error("Audience submission error:", error);

            setErrors({
                email:
                    "We could not complete your request right now. Please try again shortly.",
            });
        } finally {
            setIsSubmitting(false);
        }
    }

    return (
        <section className="w-full rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="mb-5">
                <p className="text-sm font-semibold uppercase tracking-wide text-blue-700">
                    Stay Connected
                </p>

                <h2 className="mt-1 text-2xl font-bold text-slate-900">
                    Connect with Bible Therapy Assistant
                </h2>

                <p className="mt-2 text-sm leading-6 text-slate-600">
                    Receive occasional updates about new BTA features, Bible studies,
                    devotionals, and future TAD Concepts resources.
                </p>
            </div>

            {successMessage && (
                <div className="mb-5 rounded-xl border border-green-200 bg-green-50 p-4 text-sm text-green-800">
                    {successMessage}
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-slate-800">
                        Name <span className="text-red-600">*</span>
                    </label>

                    <input
                        type="text"
                        value={formData.name}
                        onChange={(event) => updateField("name", event.target.value)}
                        className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                        placeholder="Your name"
                    />

                    {errors.name && (
                        <p className="mt-1 text-sm text-red-600">{errors.name}</p>
                    )}
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-800">
                        Email Address <span className="text-red-600">*</span>
                    </label>

                    <input
                        type="email"
                        value={formData.email}
                        onChange={(event) => updateField("email", event.target.value)}
                        className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                        placeholder="you@example.com"
                    />

                    {errors.email && (
                        <p className="mt-1 text-sm text-red-600">{errors.email}</p>
                    )}
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-800">
                        Contact Type <span className="text-red-600">*</span>
                    </label>

                    <select
                        value={formData.contactType}
                        onChange={(event) =>
                            updateField("contactType", event.target.value as ContactType | "")
                        }
                        className="mt-1 w-full rounded-xl border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                    >
                        <option value="">Select contact type</option>

                        {CONTACT_TYPES.map((type) => (
                            <option key={type} value={type}>
                                {type}
                            </option>
                        ))}
                    </select>

                    {errors.contactType && (
                        <p className="mt-1 text-sm text-red-600">{errors.contactType}</p>
                    )}
                </div>

                <div>
                    <label className="block text-sm font-medium text-slate-800">
                        Organization
                    </label>

                    <input
                        type="text"
                        value={formData.organization}
                        onChange={(event) => updateField("organization", event.target.value)}
                        className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                        placeholder="Church, ministry, business, or organization"
                    />
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                    <div>
                        <label className="block text-sm font-medium text-slate-800">
                            City
                        </label>

                        <input
                            type="text"
                            value={formData.city}
                            onChange={(event) => updateField("city", event.target.value)}
                            className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                            placeholder="City"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-800">
                            State
                        </label>

                        <input
                            type="text"
                            value={formData.state}
                            onChange={(event) => updateField("state", event.target.value)}
                            className="mt-1 w-full rounded-xl border border-slate-300 px-4 py-3 text-sm text-slate-900 outline-none focus:border-blue-600 focus:ring-2 focus:ring-blue-100"
                            placeholder="State"
                        />
                    </div>
                </div>

                <div>
                    <label className="flex items-start gap-3 rounded-xl border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
                        <input
                            type="checkbox"
                            checked={formData.consent}
                            onChange={(event) => updateField("consent", event.target.checked)}
                            className="mt-1 h-4 w-4 rounded border-slate-300"
                        />

                        <span>
                            I would like to receive occasional updates from Bible Therapy
                            Assistant and TAD Concepts.
                        </span>
                    </label>

                    {errors.consent && (
                        <p className="mt-1 text-sm text-red-600">{errors.consent}</p>
                    )}
                </div>

                <button
                    type="submit"
                    disabled={isSubmitting}
                    className="w-full rounded-xl bg-blue-700 px-5 py-3 text-sm font-semibold text-white transition hover:bg-blue-800 disabled:cursor-not-allowed disabled:bg-slate-400"
                >
                    {isSubmitting ? "Submitting..." : "Keep Me Connected"}
                </button>
            </form>
        </section>
    );
}
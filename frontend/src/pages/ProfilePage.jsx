import { useState } from "react";

import { updateProfile } from "../api/profile.js";
import useAuth from "../auth/useAuth.js";

function getProfileFormValues(user) {
  return {
    first_name: user?.first_name ?? "",
    last_name: user?.last_name ?? "",
    email: user?.email ?? "",
    residence_city: user?.residence_city ?? "",
  };
}

export default function ProfilePage() {
  const { user, updateUser } = useAuth();

  const [form, setForm] = useState(
    () => getProfileFormValues(user),
  );
  
  const [initialForm, setInitialForm] = useState(
    () => getProfileFormValues(user),
  );

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;

    setForm((current) => ({
      ...current,
      [name]: value,
    }));

    setSuccessMessage("");
  }

  function getChanges() {
    if (!initialForm) {
      return {};
    }

    const changes = {};

    for (const [field, value] of Object.entries(form)) {
      if (value !== initialForm[field]) {
        changes[field] =
          field === "residence_city" && value.trim() === ""
            ? null
            : value;
      }
    }

    return changes;
  }

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setSuccessMessage("");

    const changes = getChanges();

    if (Object.keys(changes).length === 0) {
      setSuccessMessage("No profile changes to save.");
      return;
    }

    setIsSubmitting(true);

    try {
      const response = await updateProfile(changes);

      updateUser(response.profile);

      const updatedValues =
        getProfileFormValues(response.profile);

      setForm(updatedValues);
      setInitialForm(updatedValues);

      setSuccessMessage("Profile updated successfully.");
    } catch (error) {
      setError(
        error.message || "The profile could not be updated.",
      );
    } finally {
      setIsSubmitting(false);
    }
  }

  function handleReset() {
    if (!initialForm) {
      return;
    }

    setForm(initialForm);
    setError("");
    setSuccessMessage("");
  }

  const hasChanges =
    initialForm &&
    Object.keys(form).some(
      (field) => form[field] !== initialForm[field],
    );

  return (
    <div className="profile-page">
      <header className="profile-heading">
        <div>
          <p className="eyebrow">Account</p>

          <h1>My profile</h1>

          <p>
            View your account information and update your
            personal details.
          </p>
        </div>
      </header>

      <div className="profile-layout">
        <aside className="profile-summary-card">
          <div className="profile-avatar" aria-hidden="true">
            {getInitials(user)}
          </div>

          <div className="profile-summary-name">
            <h2>
              {[user?.first_name, user?.last_name]
                .filter(Boolean)
                .join(" ") || "Spectator"}
            </h2>

            <p>{user?.email}</p>
          </div>

          <div className="profile-summary-divider" />

          <ProfileInfo
            label="Phone number"
            value={user?.phone_number}
          />

          <ProfileInfo
            label="Account type"
            value={user?.role}
          />

          {user?.account_status && (
            <ProfileInfo
              label="Account status"
              value={user.account_status}
            />
          )}

          {user?.signup_date && (
            <ProfileInfo
              label="Member since"
              value={formatDate(user.signup_date)}
            />
          )}
        </aside>

        <section className="profile-form-card">
          <div className="profile-form-heading">
            <h2>Personal information</h2>

            <p>
              Update the information associated with your
              account.
            </p>
          </div>

          <form
            className="profile-form"
            onSubmit={handleSubmit}
          >
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="profile-first-name">
                  First name
                </label>

                <input
                  id="profile-first-name"
                  name="first_name"
                  type="text"
                  value={form.first_name}
                  onChange={handleChange}
                  maxLength={50}
                  autoComplete="given-name"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="profile-last-name">
                  Last name
                </label>

                <input
                  id="profile-last-name"
                  name="last_name"
                  type="text"
                  value={form.last_name}
                  onChange={handleChange}
                  maxLength={50}
                  autoComplete="family-name"
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="profile-email">Email</label>

              <input
                id="profile-email"
                name="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                maxLength={255}
                autoComplete="email"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="profile-city">
                Residence city
                <span className="optional-label">
                  {" "}
                  (optional)
                </span>
              </label>

              <input
                id="profile-city"
                name="residence_city"
                type="text"
                value={form.residence_city}
                onChange={handleChange}
                maxLength={100}
                autoComplete="address-level2"
              />
            </div>

            <div className="profile-readonly-field">
              <div>
                <span>Phone number</span>

                <strong>
                  {user?.phone_number || "—"}
                </strong>
              </div>

              <p>
                Your phone number cannot be changed from
                your profile.
              </p>
            </div>

            {error && (
              <p className="form-error" role="alert">
                {error}
              </p>
            )}

            {successMessage && (
              <p
                className="profile-success-message"
                role="status"
              >
                {successMessage}
              </p>
            )}

            <div className="profile-actions">
              <button
                className="button button-secondary"
                type="button"
                onClick={handleReset}
                disabled={!hasChanges || isSubmitting}
              >
                Discard
              </button>

              <button
                className="button"
                type="submit"
                disabled={!hasChanges || isSubmitting}
              >
                {isSubmitting
                  ? "Saving..."
                  : "Save changes"}
              </button>
            </div>
          </form>
        </section>
      </div>
    </div>
  );
}

function ProfileInfo({ label, value }) {
  return (
    <div className="profile-summary-info">
      <span>{label}</span>
      <strong>{value || "—"}</strong>
    </div>
  );
}

function getInitials(user) {
  const first = user?.first_name?.trim()?.[0] ?? "";
  const last = user?.last_name?.trim()?.[0] ?? "";

  const initials = `${first}${last}`.toUpperCase();

  return initials || "TT";
}

function formatDate(value) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return "—";
  }

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
  }).format(date);
}
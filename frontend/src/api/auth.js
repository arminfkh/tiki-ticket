import { apiRequest } from "./client.js";

export function signup({
  phoneNumber,
  email,
  firstName,
  lastName,
  residenceCity,
  password,
}) {
  return apiRequest("/auth/signup/", {
    method: "POST",
    body: {
      phone_number: phoneNumber,
      email,
      first_name: firstName,
      last_name: lastName,
      residence_city: residenceCity || null,
      password,
    },
  });
}

export function verifySignup(email, otp) {
  return apiRequest("/auth/signup/verify/", {
    method: "POST",
    body: { email, otp },
  });
}

export function loginWithPassword(email, password) {
  return apiRequest("/auth/login/", {
    method: "POST",
    body: { email, password },
  });
}

export function requestLoginOtp(email) {
  return apiRequest("/auth/login/otp/request/", {
    method: "POST",
    body: { email },
  });
}

export function loginWithOtp(email, otp) {
  return apiRequest("/auth/login/otp/verify/", {
    method: "POST",
    body: { email, otp },
  });
}

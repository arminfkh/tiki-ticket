import ProtectedRoute from "./components/ProtectedRoute.jsx";
import MainLayout from "./layouts/MainLayout.jsx";

import HomePage from "./pages/HomePage.jsx";
import LoginPage from "./pages/LoginPage.jsx";
import SignupPage from "./pages/SignupPage.jsx";
import SignupVerifyPage from "./pages/SignupVerifyPage.jsx";
import TicketsPage from "./pages/TicketsPage.jsx";
import TicketDetailsPage from "./pages/TicketDetailsPage.jsx";
import ReservationsPage from "./pages/ReservationsPage.jsx";
import CheckoutPage from "./pages/CheckoutPage.jsx";
import ProfilePage from "./pages/ProfilePage.jsx";
import ReportPage from "./pages/ReportPage.jsx";
import SupportDashboardPage from "./pages/SupportDashboardPage.jsx";
import NotFoundPage from "./pages/NotFoundPage.jsx";
import { Navigate, Route, Routes } from "react-router";

export default function App() {
  return (
    <Routes>
      <Route element={<MainLayout />}>
        <Route index element={<HomePage />} />

        <Route path="login" element={<LoginPage />} />
        <Route path="signup" element={<SignupPage />} />
        <Route path="signup/verify" element={<SignupVerifyPage />} />

        <Route
          path="tickets"
          element={<Navigate to="/tickets/football" replace />}
        />

        <Route path="tickets/:sport" element={<TicketsPage />} />

        <Route
          path="tickets/:sport/:ticketId"
          element={<TicketDetailsPage />}
/>

        <Route element={<ProtectedRoute allowedRoles={["Spectator"]} />}>
          <Route path="reservations" element={<ReservationsPage />} />
          <Route
            path="checkout/:reservationId"
            element={<CheckoutPage />}
          />
          <Route path="profile" element={<ProfilePage />} />
          <Route path="report/:reservationId" element={<ReportPage />} />
        </Route>

        <Route element={<ProtectedRoute allowedRoles={["Support"]} />}>
          <Route path="support" element={<SupportDashboardPage />} />
        </Route>

        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}

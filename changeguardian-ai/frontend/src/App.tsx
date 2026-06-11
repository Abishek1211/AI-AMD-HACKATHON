import { useState } from "react";
import { Routes, Route, Link, useLocation } from "react-router-dom";
import { AppBar, Box, Container, Tab, Tabs, Toolbar, Typography } from "@mui/material";
import ChangeSubmission from "./pages/ChangeSubmission";
import DependencyGraph from "./pages/DependencyGraph";
import RiskAnalysis from "./pages/RiskAnalysis";
import Recommendation from "./pages/Recommendation";
import { AnalyzeChangeResponse } from "./services/api";

const NAV = [
  { label: "Submit Change", path: "/" },
  { label: "Dependencies", path: "/dependencies" },
  { label: "Risk Analysis", path: "/risk" },
  { label: "Recommendation", path: "/recommendation" },
];

export default function App() {
  const [result, setResult] = useState<AnalyzeChangeResponse | null>(null);
  const location = useLocation();
  const currentTab = NAV.findIndex((n) => n.path === location.pathname);

  return (
    <Box sx={{ minHeight: "100vh", bgcolor: "#f5f7fa" }}>
      <AppBar position="static" elevation={0} color="inherit" sx={{ borderBottom: "1px solid #e0e0e0" }}>
        <Toolbar>
          <Typography variant="h6" fontWeight={700} sx={{ mr: 4 }}>
            ChangeGuardian AI
          </Typography>
          <Tabs value={currentTab === -1 ? 0 : currentTab} textColor="primary" indicatorColor="primary">
            {NAV.map((n) => (
              <Tab key={n.path} label={n.label} component={Link} to={n.path} />
            ))}
          </Tabs>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg">
        <Routes>
          <Route path="/" element={<ChangeSubmission onResult={setResult} />} />
          <Route path="/dependencies" element={<DependencyGraph result={result} />} />
          <Route path="/risk" element={<RiskAnalysis result={result} />} />
          <Route path="/recommendation" element={<Recommendation result={result} />} />
        </Routes>
      </Container>
    </Box>
  );
}

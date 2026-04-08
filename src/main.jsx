import React, { lazy, Suspense } from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import { Provider } from "react-redux";
import App from "./App";
import { store } from "./app/store";
import "./index.css";

const Home = lazy(() => import("./routes/Home"));
const Forecast = lazy(() => import("./routes/Forecast"));
const About = lazy(() => import("./routes/About"));
const Privacy = lazy(() => import("./routes/Privacy"));
const Terms = lazy(() => import("./routes/Terms"));

const router = createBrowserRouter([
  {
    path: "/",
    element: (
      <Suspense fallback={<div className="hidden">Loading...</div>}>
        <App />
      </Suspense>
    ),

    children: [
      { index: true, element: <Home /> },
      {
        path: "forecast",
        element: <Forecast />,
      },
      { path: "about", element: <About /> },
      { path: "privacy", element: <Privacy /> },
      { path: "terms", element: <Terms /> },
    ],
  },
  {
    path: "*",
    element: <div>Not Found</div>,
  },
]);

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <Provider store={store}>
      <RouterProvider router={router} />
    </Provider>
  </React.StrictMode>
);

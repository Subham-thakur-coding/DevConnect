
(function () {
    "use strict";

    const STORAGE_KEY = "devconnect-theme";
    const VALID_THEMES = ["light", "dark"];

    function getPreferredTheme() {
        try {
            const savedTheme = localStorage.getItem(STORAGE_KEY);

            if (VALID_THEMES.includes(savedTheme)) {
                return savedTheme;
            }
        } catch (error) {
            console.warn("Unable to read the saved theme preference.", error);
        }

        return window.matchMedia &&
            window.matchMedia("(prefers-color-scheme: dark)").matches
                ? "dark"
                : "light";
    }

    function saveTheme(theme) {
        try {
            localStorage.setItem(STORAGE_KEY, theme);
        } catch (error) {
            console.warn("Unable to save the theme preference.", error);
        }
    }

    function applyTheme(theme) {
        const normalizedTheme = VALID_THEMES.includes(theme)
            ? theme
            : "light";

        document.body.dataset.theme = normalizedTheme;
        document.documentElement.dataset.theme = normalizedTheme;

        const toggle = document.getElementById("themeToggle");
        const icon = document.getElementById("themeIcon");

        const isDark = normalizedTheme === "dark";

        if (icon) {
            icon.className = isDark
                ? "bi bi-sun-fill"
                : "bi bi-moon-stars-fill";
        }

        if (toggle) {
            const label = isDark
                ? "Switch to light mode"
                : "Switch to dark mode";

            toggle.setAttribute("aria-label", label);
            toggle.setAttribute("title", label);
            toggle.setAttribute("aria-pressed", String(isDark));
        }
    }

    function initializeTheme() {
        applyTheme(getPreferredTheme());

        const toggle = document.getElementById("themeToggle");

        if (!toggle) {
            return;
        }

        toggle.addEventListener("click", function () {
            const currentTheme = document.body.dataset.theme || "light";

            const nextTheme = currentTheme === "dark"
                ? "light"
                : "dark";

            saveTheme(nextTheme);
            applyTheme(nextTheme);
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", initializeTheme);
    } else {
        initializeTheme();
    }
})();

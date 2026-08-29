if (!isLoggedIn()) {
  location.href = "/login.html";
}

document.getElementById("logout").onclick = () => {
  clearTokens();
  location.href = "/login.html";
};

apiFetch("/auth/me/").then(async (res) => {
  if (!res.ok) {
    location.href = "/login.html";
    return;
  }
  const user = await res.json();
  document.getElementById("user-email").textContent = user.email;
});

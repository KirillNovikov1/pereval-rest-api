const output = document.getElementById("output");
const statusBadge = document.getElementById("statusBadge");

const postPayload = document.getElementById("postPayload");
const patchPayload = document.getElementById("patchPayload");

postPayload.value = JSON.stringify(
  {
    beautyTitle: "пер.",
    title: "Пхия",
    other_titles: "Триев",
    connect: "",
    add_time: "2026-03-22 12:00:00",
    user: {
      email: "user@example.com",
      fam: "Иванов",
      name: "Иван",
      otc: "Иванович",
      phone: "+79990001122"
    },
    coords: {
      latitude: 45.3842,
      longitude: 7.1525,
      height: 1200
    },
    level: {
      winter: "",
      summer: "1А",
      autumn: "1А",
      spring: ""
    },
    images: [
      {
        title: "Вид на перевал",
        data: "ZmFrZS1pbWFnZS1kYXRh"
      }
    ]
  },
  null,
  2
);

patchPayload.value = JSON.stringify(
  {
    beautyTitle: "пер.",
    title: "Пхия обновленный",
    other_titles: "Триев",
    connect: "",
    add_time: "2026-03-22 12:00:00",
    user: {
      email: "user@example.com",
      fam: "Иванов",
      name: "Иван",
      otc: "Иванович",
      phone: "+79990001122"
    },
    coords: {
      latitude: 45.5,
      longitude: 7.5,
      height: 1300
    },
    level: {
      winter: "",
      summer: "1Б",
      autumn: "1А",
      spring: ""
    },
    images: [
      {
        title: "Новое фото",
        data: "bmV3LWZha2UtaW1hZ2UtZGF0YQ=="
      }
    ]
  },
  null,
  2
);

function setStatus(ok, text) {
  statusBadge.textContent = text;
  statusBadge.className = ok ? "badge success" : "badge error";
}

function showResult(data) {
  output.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
}

async function apiRequest(url, options = {}) {
  try {
    const response = await fetch(url, options);
    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    setStatus(response.ok, `${response.status} ${response.statusText}`);
    showResult(data);
  } catch (error) {
    setStatus(false, "Ошибка запроса");
    showResult(String(error));
  }
}

document.getElementById("healthBtn").addEventListener("click", () => {
  apiRequest("/health");
});

document.getElementById("getByIdBtn").addEventListener("click", () => {
  const id = document.getElementById("perevalId").value.trim();
  if (!id) {
    setStatus(false, "Нужен ID");
    showResult("Введите ID перевала.");
    return;
  }
  apiRequest(`/submitData/${id}`);
});

document.getElementById("getByEmailBtn").addEventListener("click", () => {
  const email = document.getElementById("userEmail").value.trim();
  if (!email) {
    setStatus(false, "Нужен email");
    showResult("Введите email пользователя.");
    return;
  }
  apiRequest(`/submitData?user_email=${encodeURIComponent(email)}`);
});

document.getElementById("postBtn").addEventListener("click", () => {
  try {
    const body = JSON.parse(postPayload.value);
    apiRequest("/submitData", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });
  } catch (error) {
    setStatus(false, "Некорректный JSON");
    showResult(String(error));
  }
});

document.getElementById("patchBtn").addEventListener("click", () => {
  const id = document.getElementById("patchId").value.trim();
  if (!id) {
    setStatus(false, "Нужен ID");
    showResult("Введите ID перевала для PATCH.");
    return;
  }

  try {
    const body = JSON.parse(patchPayload.value);
    apiRequest(`/submitData/${id}`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });
  } catch (error) {
    setStatus(false, "Некорректный JSON");
    showResult(String(error));
  }
});
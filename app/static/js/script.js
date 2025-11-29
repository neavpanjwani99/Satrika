// ======= CONFIG =======
let currentSession = null;
let editingChatId = null;

// DOM Elements
const chatContainer = document.getElementById("chat-container");
const userInput = document.getElementById("user-input");
const chatList = document.getElementById("chat-list");
const sidebar = document.getElementById("sidebar");
const toggleSidebarBtn = document.getElementById("toggle-sidebar");
const closeSidebarBtn = document.getElementById("close-sidebar");
const mobileOverlay = document.getElementById("mobile-overlay");
const welcomeMessage = document.getElementById("welcome-message");
const welcomeNewChatBtn = document.getElementById("welcome-new-chat");
const editChatModal = document.getElementById("edit-chat-modal");
const editChatTitle = document.getElementById("edit-chat-title");
const cancelEditBtn = document.getElementById("cancel-edit");
const saveEditBtn = document.getElementById("save-edit");

// ======= SIDEBAR FUNCTIONS (Tailwind classes use kar ke) =======
function openSidebar() {
  console.log("Opening sidebar");
  sidebar.classList.remove("-translate-x-full");
  sidebar.classList.add("translate-x-0");
  mobileOverlay.classList.remove("hidden");
}

function closeSidebar() {
  console.log("Closing sidebar");
  // Mobile par hi slide-out kare
  if (window.innerWidth <= 768) {
    sidebar.classList.add("-translate-x-full");
    sidebar.classList.remove("translate-x-0");
  }
  mobileOverlay.classList.add("hidden");
}

function toggleSidebar() {
  console.log("Toggling sidebar");
  const isOpen = sidebar.classList.contains("translate-x-0");
  if (isOpen) {
    closeSidebar();
  } else {
    openSidebar();
  }
}

// ======= MESSAGE DISPLAY =======
function updateWelcomeMessage() {
  // Sirf .message divs check karo
  const hasMessages = chatContainer.querySelector(".message") !== null;

  if (hasMessages) {
    chatContainer.classList.add("has-messages");
    chatContainer.classList.remove("no-messages");
    welcomeMessage.classList.add("hidden");
  } else {
    chatContainer.classList.remove("has-messages");
    chatContainer.classList.add("no-messages");
    welcomeMessage.classList.remove("hidden");
  }
}

function clearMessagesOnly() {
  // Welcome message ko mat hatao, sirf .message nodes remove karo
  chatContainer.querySelectorAll(".message").forEach((el) => el.remove());
}

function renderMessages(messages) {
  console.log("Rendering messages:", messages);
  clearMessagesOnly();

  if (!messages || messages.length === 0) {
    updateWelcomeMessage();
    return;
  }

  messages.forEach((msg) => {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", msg.sender);

    const bubble = document.createElement("div");
    bubble.classList.add("bubble");
    bubble.innerHTML = `<p>${msg.message}</p>`;

    messageDiv.appendChild(bubble);
    chatContainer.appendChild(messageDiv);
  });

  chatContainer.scrollTop = chatContainer.scrollHeight;
  updateWelcomeMessage();
}

// ======= CHAT MANAGEMENT =======
function createChatItem(chat) {
  const li = document.createElement("li");
  li.classList.add("chat-item");
  if (chat.id === currentSession) {
    li.classList.add("active");
  }

  li.innerHTML = `
    <div class="chat-title flex-1 truncate mr-2">${chat.title}</div>
    <div class="chat-actions">
      <button class="chat-action-btn edit-chat" data-id="${chat.id}" title="Edit title">
        <i class="fas fa-edit text-xs"></i>
      </button>
      <button class="chat-action-btn delete-chat" data-id="${chat.id}" title="Delete chat">
        <i class="fas fa-trash text-xs"></i>
      </button>
    </div>
  `;

  // Click to load chat (agar actions pe click nahi hua ho to)
  li.addEventListener("click", (e) => {
    if (!e.target.closest(".chat-actions")) {
      console.log("Loading chat:", chat.id);
      loadChat(chat.id);
    }
  });

  // Edit button
  li.querySelector(".edit-chat").addEventListener("click", (e) => {
    e.stopPropagation();
    console.log("Editing chat:", chat.id);
    openEditModal(chat.id, chat.title);
  });

  // Delete button
  li.querySelector(".delete-chat").addEventListener("click", (e) => {
    e.stopPropagation();
    console.log("Deleting chat:", chat.id);
    deleteChat(chat.id);
  });

  return li;
}

async function loadChatList() {
  try {
    console.log("Loading chat list.");
    const res = await fetch("/list_chats");
    if (!res.ok) throw new Error("Failed to load chats");

    const chats = await res.json();
    console.log("Loaded chats:", chats);
    chatList.innerHTML = "";

    if (!chats || chats.length === 0) {
      const emptyMsg = document.createElement("li");
      emptyMsg.className =
        "text-gray-500 text-sm text-center py-4";
      emptyMsg.textContent = "No chats yet";
      chatList.appendChild(emptyMsg);
      return;
    }

    // Newest first
    chats.sort(
      (a, b) =>
        new Date(b.timestamp || b.created_at) -
        new Date(a.timestamp || a.created_at)
    );

    chats.forEach((chat) => {
      const chatItem = createChatItem(chat);
      chatList.appendChild(chatItem);
    });
  } catch (error) {
    console.error("Error loading chat list:", error);
    chatList.innerHTML =
      '<li class="text-red-500 text-sm text-center py-4">Error loading chats</li>';
  }
}

async function startNewChat() {
  try {
    console.log("Starting new chat.");
    const res = await fetch("/new_chat", { method: "POST" });
    if (!res.ok) throw new Error("Failed to create chat");

    const chat = await res.json();
    console.log("New chat created:", chat);
    currentSession = chat.id;

    // Clear chat area (sirf messages) and show welcome
    clearMessagesOnly();
    updateWelcomeMessage();
    userInput.value = "";

    await loadChatList();

    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
      closeSidebar();
    }

    userInput.focus();
  } catch (error) {
    console.error("Error creating new chat:", error);
    alert("Error creating new chat");
  }
}

async function loadChat(session_id) {
  try {
    console.log("Loading chat:", session_id);
    const res = await fetch(`/load_chat/${session_id}`);
    if (!res.ok) throw new Error("Failed to load chat");

    const chat = await res.json();
    console.log("Loaded chat data:", chat);

    currentSession = session_id;
    renderMessages(chat.messages || []);
    await loadChatList();

    // Close sidebar on mobile
    if (window.innerWidth <= 768) {
      closeSidebar();
    }

    userInput.focus();
  } catch (error) {
    console.error("Error loading chat:", error);
    alert("Error loading chat: " + error.message);
  }
}

async function deleteChat(session_id) {
  if (!confirm("Are you sure you want to delete this chat?")) {
    return;
  }

  try {
    console.log("Deleting chat:", session_id);
    const res = await fetch(`/delete_chat/${session_id}`, {
      method: "DELETE",
    });

    if (res.ok) {
      // If deleting current chat, clear UI
      if (currentSession === session_id) {
        currentSession = null;
        clearMessagesOnly();
        updateWelcomeMessage();
      }

      await loadChatList();
    } else {
      throw new Error("Failed to delete chat");
    }
  } catch (error) {
    console.error("Error deleting chat:", error);
    alert("Error deleting chat");
  }
}

// ======= EDIT MODAL FUNCTIONS =======
function openEditModal(chatId, currentTitle) {
  editingChatId = chatId;
  editChatTitle.value = currentTitle;
  editChatModal.classList.remove("hidden");
  editChatTitle.focus();
}

function closeEditModal() {
  editingChatId = null;
  editChatTitle.value = "";
  editChatModal.classList.add("hidden");
}

async function updateChatTitle() {
  if (!editingChatId || !editChatTitle.value.trim()) {
    alert("Please enter a valid title");
    return;
  }

  try {
    const res = await fetch(`/update_chat/${editingChatId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: editChatTitle.value.trim() }),
    });

    if (res.ok) {
      await loadChatList();
      closeEditModal();
    } else {
      throw new Error("Failed to update chat title");
    }
  } catch (error) {
    console.error("Error updating chat title:", error);
    alert("Error updating chat title");
  }
}

// ======= MESSAGE SENDING =======
async function sendMessage() {
  const message = userInput.value.trim();
  if (!message) {
    alert("Please enter a message");
    return;
  }

  // If no current session, create one first
  if (!currentSession) {
    await startNewChat();
    // slight delay, just in case
    await new Promise((resolve) => setTimeout(resolve, 100));
  }

  console.log("Sending message to session:", currentSession);

  // Show user message immediately
  const userMessageDiv = document.createElement("div");
  userMessageDiv.classList.add("message", "user");

  const userBubble = document.createElement("div");
  userBubble.classList.add("bubble");
  userBubble.innerHTML = `<p>${message}</p>`;

  userMessageDiv.appendChild(userBubble);
  chatContainer.appendChild(userMessageDiv);

  userInput.value = "";
  chatContainer.scrollTop = chatContainer.scrollHeight;
  updateWelcomeMessage();

  try {
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: currentSession,
        message: message,
      }),
    });

    if (!res.ok) throw new Error("Failed to send message");

    const data = await res.json();
    console.log("Bot response:", data);

    // Bot message
    const botMessageDiv = document.createElement("div");
    botMessageDiv.classList.add("message", "bot");

    const botBubble = document.createElement("div");
    botBubble.classList.add("bubble");
    botBubble.innerHTML = `<p>${data.reply}</p>`;

    botMessageDiv.appendChild(botBubble);
    chatContainer.appendChild(botMessageDiv);

    chatContainer.scrollTop = chatContainer.scrollHeight;
    await loadChatList(); // Refresh sidebar titles
  } catch (error) {
    console.error("Error sending message:", error);

    const errorMessageDiv = document.createElement("div");
    errorMessageDiv.classList.add("message", "bot");

    const errorBubble = document.createElement("div");
    errorBubble.classList.add("bubble");
    errorBubble.innerHTML =
      '<p class="text-red-400">Sorry, there was an error. Please try again.</p>';

    errorMessageDiv.appendChild(errorBubble);
    chatContainer.appendChild(errorMessageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }
}

// ======= QUICK ACTIONS =======
function setupQuickActions() {
  document.querySelectorAll(".quick-action-btn").forEach((btn) => {
    btn.addEventListener("click", function () {
      const action = this.dataset.action;
      let message = "";

      switch (action) {
        case "write-copy":
          message =
            "Help me write compelling copy for my product launch";
          break;
        case "create-avatar":
          message =
            "Create an AI avatar for my social media profile";
          break;
      }

      if (message) {
        userInput.value = message;
        userInput.focus();
      }
    });
  });
}

// ======= EVENT LISTENERS =======
function setupEventListeners() {
  console.log("Setting up event listeners.");

  // Buttons
  document
    .getElementById("send-btn")
    .addEventListener("click", sendMessage);
  document
    .getElementById("new-chat-btn")
    .addEventListener("click", startNewChat);
  welcomeNewChatBtn.addEventListener("click", startNewChat);
  toggleSidebarBtn.addEventListener("click", toggleSidebar);
  closeSidebarBtn.addEventListener("click", closeSidebar);

  // Modal buttons
  cancelEditBtn.addEventListener("click", closeEditModal);
  saveEditBtn.addEventListener("click", updateChatTitle);

  // Input Enter key
  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  });

  // Overlay click to close sidebar
  mobileOverlay.addEventListener("click", closeSidebar);

  // Escape key to close modal / sidebar
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (!editChatModal.classList.contains("hidden")) {
        closeEditModal();
      } else if (
        window.innerWidth <= 768 &&
        sidebar.classList.contains("translate-x-0")
      ) {
        closeSidebar();
      }
    }
  });

  // Click outside modal to close
  editChatModal.addEventListener("click", (e) => {
    if (e.target === editChatModal) {
      closeEditModal();
    }
  });
}

// ======= INITIALIZATION =======
async function initializeApp() {
  console.log("Initializing app.");

  setupEventListeners();
  setupQuickActions();
  updateWelcomeMessage();

  try {
    // Load chat list first
    await loadChatList();

    // Try to load the most recent chat
    const res = await fetch("/list_chats");
    const chats = await res.json();

    if (chats && chats.length > 0) {
      const mostRecentChat = chats.sort(
        (a, b) =>
          new Date(b.timestamp || b.created_at) -
          new Date(a.timestamp || a.created_at)
      )[0];
      await loadChat(mostRecentChat.id);
    } else {
      // No chats exist, create a new one
      await startNewChat();
    }
  } catch (error) {
    console.error("Error during initialization:", error);
    await startNewChat();
  }
}

// Start the app when page loads
window.addEventListener("load", initializeApp);

// Handle window resize for responsive sidebar
window.addEventListener("resize", () => {
  if (window.innerWidth > 768) {
    // Desktop: Tailwind ka md:translate-x-0 handle karega
    sidebar.classList.remove("-translate-x-full", "translate-x-0");
    mobileOverlay.classList.add("hidden");
  } else {
    // Mobile: agar open nahi hai to hidden rakho
    if (!sidebar.classList.contains("translate-x-0")) {
      sidebar.classList.add("-translate-x-full");
    }
  }
});


const chatArea = document.getElementById('chat-area');
const messageInput = document.getElementById('message-input');
const chatbot = document.getElementById('chatbot');
const chatbotBtn = document.getElementById('chatbot-btn');
const closeChatbotBtn = document.getElementById('close-chatbot');
const ticketForm = document.querySelector('#ticket form');
const bookNowBtn = document.querySelector('#book-now-btn');
const museumCards = document.querySelectorAll('#ticket .card');
const ticketTypeContainer = document.getElementById('ticket-type-container');
const visitDateContainer = document.getElementById('visit-date-container');

// Ensure all elements are found before adding event listeners
if (chatbotBtn) {
  chatbotBtn.addEventListener('click', toggleChatbotVisibility);
} else {
  console.error('Chatbot button not found');
}

if (closeChatbotBtn) {
  closeChatbotBtn.addEventListener('click', () => {
    chatbot.classList.add('hidden');
    chatbot.classList.remove('visible');
  });
}// Function to toggle text and loader visibility
function set_debugging(){
  fetch("/debugger_on", {
    method: 'POST'  // Ensure this matches the Flask route method
  })
  .then(response => response.json())
  .then(data => {
    console.log('Response from Flask:', data);
  })
  .catch(error => {
    console.error('Error calling Flask route:', error);
  });
}

// Function to filter museum cards based on search input
function filterCards() {
  const searchInput = document.getElementById('search').value.toLowerCase();
  const museumCards = document.querySelectorAll('#museum-cards .card');
  
  museumCards.forEach(card => {
    const museumName = card.dataset.name.toLowerCase();
    if (museumName.includes(searchInput)) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}


// Function to toggle the visibility of the "Book Now" button and loader
function tuggler() {
  console.log('Toggler function called');  // Debugging line
  const textElement = document.getElementById('botton_text');
  const loaderElement = document.getElementById('botton_loader');
  const ticketer = document.getElementById('ticket');
  const set = document.getElementById('set');
  if (textElement && loaderElement) {
    // Toggle visibility
    textElement.classList.toggle('hidden');
    textElement.classList.toggle('block');
    loaderElement.classList.toggle('hidden');
    loaderElement.classList.toggle('block');
    setTimeout(() => {
      ticketer.style.display = 'none';
      set.style.display = 'block';
    }, 2000);
  } else {
    console.error('Elements not found');
  }
}

// Function to adjust chatbot size and ensure responsiveness
function adjustChatbotSize() {
  const buttonRect = chatbotBtn.getBoundingClientRect();
  const viewportWidth = window.innerWidth;
  if (viewportWidth <= 768) {
    chatbot.style.width = '90vw';
    chatbot.style.height = '50vh';
    chatbot.style.right = '10px';
    chatbot.style.bottom = '80px';
  } else {
    chatbot.style.width = '500px';
    chatbot.style.height = `${Math.max(buttonRect.top - 20, 300)}px`;
    chatbot.style.right = '40px';
  }
}

// Toggle chatbot visibility
function toggleChatbotVisibility() {
  console.log('Chatbot button clicked'); // Debugging line
  chatbot.classList.toggle('hidden');
  chatbot.classList.toggle('visible');
  adjustChatbotSize();
}

// Function to handle the "Enter" key to send a message
function handleEnter(event) {
  if (event.key === 'Enter') {
    sendMessage();
  }
}

// Function to handle form interactions
function handleFormInteraction() {
  const museumSelected = document.querySelector('input[name="museum"]');  // Check for 'museum' input instead
  console.log('Museum selected:', museumSelected ? museumSelected.value : 'None');
  bookNowBtn.disabled = !museumSelected;  // Enable button if a museum is selected
}


// Function to handle museum selection
function selectMuseum(museumName) {
  museumCards.forEach(card => card.classList.remove('selected'));
  const selectedCard = Array.from(museumCards).find(card => card.querySelector('h3').textContent === museumName);
  if (selectedCard) {
    selectedCard.classList.add('selected');
    const museumInput = document.createElement('input');
    museumInput.type = 'hidden';
    museumInput.name = 'museum';
    museumInput.value = museumName;
    ticketForm.appendChild(museumInput);

    // Fetch request to the Flask route
    fetch(`/selector/${encodeURIComponent(museumName)}`, {
      method: 'POST'  // Ensure this matches the Flask route method
    })
    .then(response => response.json())
    .then(data => {
      console.log('Response from Flask:', data);
    })
    .catch(error => {
      console.error('Error calling Flask route:', error);
    });

    // Show ticket type and date selector
    handleFormInteraction();
  }
}

// Function to reset the form
function resetForm() {
  ticketForm.reset();
  bookNowBtn.disabled = true;
  document.querySelectorAll('input[name="museum-cards"]').forEach(input => input.remove());
  museumCards.forEach(card => card.classList.remove('selected'));
}

// Function to send a message
function sendMessage() {
  const messageText = messageInput.value.trim();
  if (messageText !== '') {
    // Create new chat bubble for the user's message
    const userMessage = document.createElement('div');
    userMessage.classList.add('flex', 'items-start', 'justify-end', 'space-x-3', 'mb-4', 'user-message', 'animate-slideInRight');
    userMessage.innerHTML = `
      <div class="bg-blue-200 text-white p-4 rounded-xl shadow-md max-w-xs mr-4">
        <p>${messageText}</p>
      </div>
      <div class="w-12 h-12 rounded-full bg-blue-100 text-white flex justify-center items-center text-2xl">🧐</div>
    `;

    // Insert the user's message into the chat area
    chatArea.appendChild(userMessage);
    // Clear the message input field
    messageInput.value = '';
    // Scroll the chat area to the bottom to show the new message
    chatArea.scrollTop = chatArea.scrollHeight;

    // Simulate bot response with a slight delay
    fetch('/chatbot', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: messageText})
    })
    .then(response => response.json())
    .then(data => {
      let botMessageText = "Sorry! I couldn't understand";  // Default response in case of error
      if (data.response) {
        botMessageText = data.response;
        if (data.function) {
          func_caller(data.function);
        }
      }
      // Show the bot's message after a delay
      setTimeout(() => {
        const botMessage = document.createElement('div');
        botMessage.classList.add('flex', 'items-start', 'space-x-2', 'mb-4', 'bot-message', 'animate-slideInRight');
        botMessage.innerHTML = `
          <div class="w-12 h-12 rounded-full bg-blue-400 text-white flex justify-center items-center text-2xl">🏛️</div>
          <div class="bg-blue-100 p-4 rounded-xl shadow-lg max-w-xs text-blue-800">
            <p>${botMessageText}</p>
          </div>
        `;
        chatArea.appendChild(botMessage);
        chatArea.scrollTop = chatArea.scrollHeight;
      }, 1000);  // Bot response delay
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }
}

// Function to handle bot response actions
function func_caller(botResponse) {
  if (botResponse === 'ticket_book') {
    const ticket = document.getElementById('ticket');
    ticket.style.display = 'block';
    chatbot.classList.add('hidden');
    resetForm(); // Reset and disable form when opening ticket section
  }
}

// Add event listeners for form inputs
document.querySelectorAll('#ticket input, #ticket select').forEach(input => {
  input.addEventListener('input', handleFormInteraction);
});

// Add event listeners for museum cards
museumCards.forEach(card => {
  card.addEventListener('click', function() {
    selectMuseum(this.querySelector('h3').textContent);
  });
});

// Form submission handler
ticketForm.addEventListener('submit', function(event) {
  event.preventDefault();
  const selectedMuseum = document.querySelector('input[name="museum"]');
  
  // Create a new FormData object and append only the selected museum name
  const formData = new FormData();
  if (selectedMuseum) {
    formData.append('museum', selectedMuseum.value);
  }

  // Fetch request to submit the form with only the selected museum
  fetch('/ticketbook', {
    method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(data => {
    console.log('Form submitted successfully:', data);
  })
  .catch(error => {
    console.error('Error submitting form:', error);
  });
});

// Function to handle the "Enter" key to send a message
messageInput.addEventListener('keypress', handleEnter);
document.addEventListener('DOMContentLoaded', () => {
  const visitDateInput = document.getElementById('visit-date');

  // Initialize Flatpickr with custom options
  const calendar = flatpickr(visitDateInput, {
    dateFormat: 'Y-m-d',
    minDate: 'today', // Disable past dates
    onOpen: updateDisabledDates, // Update disabled dates on calendar open
    onChange: updateDisabledDates, // Update disabled dates on date change
  });

  // Function to dynamically disable dates
  function updateDisabledDates() {
    const museumName = encodeURIComponent(document.querySelector('input[name="museum"]').value);
    
    fetch(`/get-closed-dates/${museumName}`)
      .then(response => response.json())
      .then(data => {
        console.log('Data received from server:', data);  // Debugging line
        
        const closedDates = data.closed_dates;
  
        if (Array.isArray(closedDates)) {
          const validDates = closedDates.map(dayName => {
            const today = new Date();
            let dateObj;
            
            switch(dayName.toLowerCase()) {
              case 'monday':
                dateObj = new Date(today.setDate(today.getDate() + (1 + 7 - today.getDay()) % 7));  // Next Monday
                break;
              case 'tuesday':
                dateObj = new Date(today.setDate(today.getDate() + (2 + 7 - today.getDay()) % 7));  // Next Tuesday
                break;
              case 'wednesday':
                dateObj = new Date(today.setDate(today.getDate() + (3 + 7 - today.getDay()) % 7));  // Next Wednesday
                break;
              case 'thursday':
                dateObj = new Date(today.setDate(today.getDate() + (4 + 7 - today.getDay()) % 7));  // Next Thursday
                break;
              case 'friday':
                dateObj = new Date(today.setDate(today.getDate() + (5 + 7 - today.getDay()) % 7));  // Next Friday
                break;
              case 'saturday':
                dateObj = new Date(today.setDate(today.getDate() + (6 + 7 - today.getDay()) % 7));  // Next Saturday
                break;
              case 'sunday':
                dateObj = new Date(today.setDate(today.getDate() + (7 - today.getDay()) % 7));  // Next Sunday
                break;
              default:
                console.error('Invalid day string:', dayName);
                dateObj = null;
            }
  
            return dateObj && !isNaN(dateObj.getTime()) ? dateObj.toISOString().split('T')[0] : null;
          }).filter(date => date !== null);  // Remove invalid dates
          
          console.log('Closed dates processed:', validDates);  // Debugging line
  
          if (validDates.length > 0) {
            flatpickr("#visit-date", {
              disable: validDates
            });
          }
        } else {
          console.error('Expected closed_dates to be an array, but got:', closedDates);
        }
      })
      .catch(error => {
        console.error('Error fetching closed dates:', error);
      });
  }
  
  
  
});


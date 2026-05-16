document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.querySelector('#chat-form');
    const chatInput = document.querySelector('#chat-input');
    const chatMessages = document.querySelector('#chat-messages');

    const responses = {
        hello: 'Hello! Welcome to Oceanix. Ask me about plant care, price comparisons, or delivery options.',
        price: 'Our price comparison engine shows the best value across trusted sellers. See the product page for competitor pricing.',
        delivery: 'We usually deliver within 2-4 business days. Express support is available through WhatsApp.',
        ai: 'AI care tips are available for each product and can guide you on watering, light, and soil needs.',
        support: 'For instant support, click the WhatsApp icon at the bottom of the site.',
    };

    function addMessage(sender, text) {
        const message = document.createElement('div');
        message.className = `chat-message ${sender}`;
        message.textContent = text;
        chatMessages.appendChild(message);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function findResponse(text) {
        const lower = text.toLowerCase();
        if (lower.includes('hello') || lower.includes('hi')) return responses.hello;
        if (lower.includes('price') || lower.includes('compare')) return responses.price;
        if (lower.includes('delivery') || lower.includes('shipping')) return responses.delivery;
        if (lower.includes('ai') || lower.includes('smart')) return responses.ai;
        if (lower.includes('support') || lower.includes('help')) return responses.support;
        return 'Thanks for your question! Please browse the product detail pages or contact WhatsApp for personalized help.';
    }

    if (chatForm) {
        chatForm.addEventListener('submit', function (event) {
            event.preventDefault();
            const input = chatInput.value.trim();
            if (!input) return;
            addMessage('user', input);
            chatInput.value = '';
            setTimeout(function () {
                addMessage('bot', findResponse(input));
            }, 500);
        });
    }
});

// J.A.R.V.I.S. AI OS Landing Page Interactive JavaScript

document.addEventListener('DOMContentLoaded', () => {
    // 1. Tab Switching Logic for Live Demo Section
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetTab = btn.getAttribute('data-tab');
            document.getElementById(targetTab).classList.add('active');
        });
    });

    // 2. Interactive AI Email Draft Button Simulation
    const btnDraftEmail = document.getElementById('btn-draft-email');
    const emailDraftText = document.getElementById('email-draft-text');

    if (btnDraftEmail && emailDraftText) {
        btnDraftEmail.addEventListener('click', () => {
            btnDraftEmail.innerText = "Drafting with AI...";
            setTimeout(() => {
                emailDraftText.innerHTML = "<em>\"Hi Jane,<br><br>I noticed Acme Enterprise Corp is scaling its AI workflow pipeline. J.A.R.V.I.S. AI OS provides multi-tenant isolated workspaces, automated lead scoring, and RAG knowledge query. Would you be open for a 10-minute demo this Thursday?<br><br>Best regards,<br>Jarvis Sales Co-Pilot\"</em>";
                btnDraftEmail.innerText = "Re-Draft Email";
            }, 800);
        });
    }

    // 3. CTA Pricing Tier Click Handling
    const tiers = ['free', 'pro', 'biz'];
    tiers.forEach(tier => {
        const btn = document.getElementById(`btn-tier-${tier}`);
        if (btn) {
            btn.addEventListener('click', () => {
                alert(`Thank you for selecting the ${tier.toUpperCase()} Plan! Redirecting to J.A.R.V.I.S. Beta Workspace Signup...`);
            });
        }
    });
});

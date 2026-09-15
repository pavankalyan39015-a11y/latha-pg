// Latha PG Manager - Modern Tech Gradient Frontend Controller

const API_BASE = '/api/v1';

// Global State Cache
let state = {
  activeTab: 'overview',
  rooms: [],
  tenants: [],
  invoices: [],
  payments: [],
  tickets: [],
  meals: [],
  selectedMealDay: 'MONDAY',
  summary: null,
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  switchTab('overview');
  refreshAllData();

  // Set default check-in and due dates
  const today = new Date().toISOString().split('T')[0];
  const checkinInput = document.getElementById('onboard-checkin-date');
  if (checkinInput) checkinInput.value = today;

  const dueDateInput = document.getElementById('invoice-due-date');
  if (dueDateInput) {
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 7);
    dueDateInput.value = nextWeek.toISOString().split('T')[0];
  }
});

// Toast Notification Helper
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  const bgStyle = type === 'success' 
    ? 'bg-gradient-to-r from-emerald-600 to-teal-600 border border-emerald-400/40 text-white shadow-emerald-950/50' 
    : type === 'error' 
    ? 'bg-gradient-to-r from-rose-600 to-pink-600 border border-rose-400/40 text-white shadow-rose-950/50' 
    : 'bg-slate-900/90 border border-indigo-500/40 text-indigo-200 shadow-slate-950/50';

  toast.className = `${bgStyle} backdrop-blur-xl px-4 py-3 rounded-xl shadow-2xl text-xs font-semibold flex items-center gap-2.5 transform transition-all duration-300 translate-y-4 opacity-0`;
  toast.innerHTML = `
    <span class="w-2 h-2 rounded-full ${type === 'success' ? 'bg-emerald-300' : type === 'error' ? 'bg-rose-300' : 'bg-indigo-300'} animate-ping"></span>
    <span>${message}</span>
  `;

  container.appendChild(toast);

  // Smooth entrance
  requestAnimationFrame(() => {
    toast.classList.remove('translate-y-4', 'opacity-0');
  });

  setTimeout(() => {
    toast.classList.add('opacity-0', 'translate-y-2');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Tab Switching with Smooth Animations
function switchTab(tabName) {
  state.activeTab = tabName;

  // Update Desktop Navigation
  document.querySelectorAll('[data-tab-btn]').forEach(btn => {
    if (btn.getAttribute('data-tab-btn') === tabName) {
      btn.className = 'w-full flex items-center gap-3.5 px-4 py-3 rounded-xl transition text-left active bg-[#0B4F9C] text-white font-extrabold border-l-4 border-[#FFD200] shadow-md';
    } else {
      btn.className = 'w-full flex items-center gap-3.5 px-4 py-3 rounded-xl transition text-left text-blue-100 hover:bg-[#0B4F9C]/50 hover:text-white font-semibold';
    }
  });

  // Update Mobile Navigation
  document.querySelectorAll('[data-mobile-tab]').forEach(btn => {
    if (btn.getAttribute('data-mobile-tab') === tabName) {
      btn.className = 'mobile-tab-btn active flex flex-col items-center justify-center flex-1 py-1 text-[#FFD200] font-black transition-all duration-200 scale-105';
    } else {
      btn.className = 'mobile-tab-btn flex flex-col items-center justify-center flex-1 py-1 text-blue-200 hover:text-white transition-all duration-200 font-bold';
    }
  });

  // Close Mobile Drawer
  toggleSidebar(false);

  // Tab Content Visibility & Transitions
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
  });
  const targetTab = document.getElementById(`tab-${tabName}`);
  if (targetTab) targetTab.classList.add('active');

  // Page Header Titles
  const titles = {
    overview: ['Executive Overview', 'Live occupancy, revenue, and PG operations'],
    rooms: ['Room Allocations', '2, 3, and 4-sharing rooms with attached bathrooms'],
    tenants: ['Tenant Registry', 'Guest records, KYC verifications, and room assignments'],
    billing: ['Billing & Collections', 'Monthly rent invoices, payment receipts, and balance dues'],
    complaints: ['Maintenance Requests', 'Plumbing, electrical, Wi-Fi, and cleaning service tickets'],
    meals: ['Mess & Meal Schedule', 'Weekly food menu and kitchen attendance headcount'],
  };

  if (titles[tabName]) {
    const titleEl = document.getElementById('page-title');
    const subtitleEl = document.getElementById('page-subtitle');
    if (titleEl) titleEl.innerText = titles[tabName][0];
    if (subtitleEl) subtitleEl.innerText = titles[tabName][1];
  }

  // Refresh tab-specific data
  if (tabName === 'overview') loadOverview();
  else if (tabName === 'rooms') loadRooms();
  else if (tabName === 'tenants') loadTenants();
  else if (tabName === 'billing') loadBilling();
  else if (tabName === 'complaints') loadComplaints();
  else if (tabName === 'meals') loadMeals();

  if (window.lucide) lucide.createIcons();
}

// Modal Handlers
function openModal(id) {
  const modal = document.getElementById(id);
  if (!modal) return;
  modal.classList.remove('hidden');

  if (id === 'modal-onboard') loadAvailableBedsDropdown();
  if (id === 'modal-payment' || id === 'modal-invoice' || id === 'modal-attendance') loadTenantsDropdown();
  if (window.lucide) lucide.createIcons();
}

function closeModal(id) {
  const modal = document.getElementById(id);
  if (modal) modal.classList.add('hidden');
}

// Refresh all cache
async function refreshAllData() {
  await Promise.all([
    loadOverview(),
    loadRooms(),
    loadTenants(),
    loadBilling(),
    loadComplaints(),
    loadMeals(),
  ]);
}

// ----------------------------------------------------
// 1. OVERVIEW TAB
// ----------------------------------------------------
async function loadOverview() {
  try {
    const res = await fetch(`${API_BASE}/dashboard/summary`);
    const data = await res.json();
    state.summary = data;

    // Stat Cards
    const elOcc = document.getElementById('stat-occupancy-rate');
    if (elOcc) elOcc.innerText = `${data.occupancy_rate_percent}%`;

    const elOccBeds = document.getElementById('stat-occupied-beds');
    if (elOccBeds) elOccBeds.innerText = `${data.occupied_beds}/${data.total_beds} beds`;

    const elBar = document.getElementById('stat-occupancy-bar');
    if (elBar) elBar.style.width = `${data.occupancy_rate_percent}%`;

    const elAvail = document.getElementById('stat-available-beds');
    if (elAvail) elAvail.innerText = data.available_beds;

    const elColl = document.getElementById('stat-collected');
    if (elColl) elColl.innerText = `₹${data.total_collected_amount.toLocaleString('en-IN')}`;

    const elBilled = document.getElementById('stat-billed');
    if (elBilled) elBilled.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-purple-400"></span> Total Billed: ₹${data.total_billed_amount.toLocaleString('en-IN')}`;

    const elDues = document.getElementById('stat-dues');
    if (elDues) elDues.innerText = `₹${data.total_outstanding_dues.toLocaleString('en-IN')}`;

    // Recent checked-in tenants
    const tenantsRes = await fetch(`${API_BASE}/tenants?is_active=true`);
    const tenants = await tenantsRes.json();
    const tbody = document.getElementById('overview-tenants-tbody');
    if (tbody) {
      if (tenants.length === 0) {
        tbody.innerHTML = `<tr><td colspan="4" class="px-6 py-4 text-center text-slate-500 text-xs">No active residents recorded yet.</td></tr>`;
      } else {
        tbody.innerHTML = tenants.slice(0, 5).map(t => `
          <tr class="hover:bg-blue-50/60 transition">
            <td class="px-6 py-4 font-bold text-[#062B63]">${t.full_name}</td>
            <td class="px-6 py-4">
              <span class="px-2.5 py-1 rounded-lg bg-[#0B4F9C]/10 text-[#0B4F9C] border border-[#0B4F9C]/30 font-extrabold text-2xs">
                ${t.bed ? t.bed.bed_number : 'Unassigned'}
              </span>
            </td>
            <td class="px-6 py-4 text-slate-600 font-mono text-xs font-semibold">${t.phone}</td>
            <td class="px-6 py-4">
              <span class="px-2.5 py-1 rounded-full text-2xs font-extrabold border ${t.kyc_status === 'VERIFIED' ? 'bg-[#10A875]/15 text-[#10A875] border-[#10A875]/30' : 'bg-[#F36C00]/15 text-[#F36C00] border-[#F36C00]/30'}">
                ${t.kyc_status}
              </span>
            </td>
          </tr>
        `).join('');
      }
    }

    // Urgent Tickets
    const ticketsRes = await fetch(`${API_BASE}/complaints?status=OPEN`);
    const tickets = await ticketsRes.json();
    const ticketsContainer = document.getElementById('overview-tickets-list');
    const ticketsCount = document.getElementById('overview-tickets-count');
    if (ticketsCount) ticketsCount.innerText = `${tickets.length} Open`;

    if (ticketsContainer) {
      if (tickets.length === 0) {
        ticketsContainer.innerHTML = `<p class="text-xs text-slate-400 py-3 text-center">No pending maintenance alerts. All facilities clear!</p>`;
      } else {
        ticketsContainer.innerHTML = tickets.slice(0, 3).map(tk => `
          <div class="p-3.5 rounded-xl border border-slate-200 bg-[#EAF3FA]/60 hover:bg-[#EAF3FA] flex items-start justify-between transition">
            <div>
              <p class="font-bold text-[#062B63] text-xs">${tk.title}</p>
              <p class="text-slate-500 text-2xs mt-0.5 font-semibold">${tk.category} &bull; #${tk.ticket_number}</p>
            </div>
            <span class="px-2 py-0.5 rounded-full text-2xs font-extrabold border ${tk.priority === 'URGENT' || tk.priority === 'HIGH' ? 'bg-[#F21F26]/15 text-[#F21F26] border-[#F21F26]/30' : 'bg-[#F36C00]/15 text-[#F36C00] border-[#F36C00]/30'}">
              ${tk.priority}
            </span>
          </div>
        `).join('');
      }
    }

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Error loading overview:', err);
  }
}

// ----------------------------------------------------
// 2. ROOMS & BEDS TAB
// ----------------------------------------------------
async function loadRooms() {
  try {
    const acFilter = document.getElementById('filter-room-ac')?.value || '';
    const floorFilter = document.getElementById('filter-room-floor')?.value || '';

    let url = `${API_BASE}/rooms?`;
    if (acFilter) url += `has_ac=${acFilter}&`;
    if (floorFilter) url += `floor=${floorFilter}&`;

    const res = await fetch(url);
    const rooms = await res.json();
    state.rooms = rooms;

    const grid = document.getElementById('rooms-grid');
    if (!grid) return;

    if (rooms.length === 0) {
      grid.innerHTML = `<div class="col-span-3 text-center py-16 text-slate-400 text-xs">No rooms found. Click "+ Add Room" to create one.</div>`;
      return;
    }

    grid.innerHTML = rooms.map(room => {
      const bedsHtml = room.beds.map(bed => {
        let badgeColor = 'bg-[#10A875]/10 border-[#10A875]/30 text-[#10A875]';
        let dotColor = 'bg-[#10A875]';
        if (bed.status === 'OCCUPIED') {
          badgeColor = 'bg-[#0B4F9C]/10 border-[#0B4F9C]/30 text-[#0B4F9C]';
          dotColor = 'bg-[#0B4F9C]';
        } else if (bed.status === 'MAINTENANCE') {
          badgeColor = 'bg-[#F36C00]/10 border-[#F36C00]/30 text-[#F36C00]';
          dotColor = 'bg-[#F36C00]';
        }

        return `
          <div class="px-3 py-2 rounded-xl border ${badgeColor} flex items-center justify-between text-xs font-bold">
            <span class="flex items-center gap-2">
              <span class="w-2 h-2 rounded-full ${dotColor}"></span>
              ${bed.bed_number}
            </span>
            <span class="text-2xs uppercase tracking-wider font-extrabold opacity-90">${bed.status}</span>
          </div>
        `;
      }).join('');

      const vacantCount = room.beds.filter(b => b.status === 'AVAILABLE').length;

      return `
        <div class="brand-card rounded-2xl p-6 space-y-4 hover:-translate-y-1.5 transition-all duration-300">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2">
                <h4 class="text-lg font-black text-[#062B63]">Room ${room.room_number}</h4>
                <span class="text-2xs font-extrabold px-2 py-0.5 rounded-full bg-[#EAF3FA] text-[#062B63] border border-blue-200">Floor ${room.floor}</span>
              </div>
              <p class="text-xs text-[#0B4F9C] font-bold mt-1">${room.room_type} &bull; ₹${room.base_rent.toLocaleString('en-IN')}/bed</p>
            </div>
            <span class="px-2.5 py-1 rounded-full text-2xs font-extrabold border ${room.has_ac ? 'bg-[#0B4F9C]/15 text-[#0B4F9C] border-[#0B4F9C]/30' : 'bg-slate-100 text-slate-600 border-slate-200'}">
              ${room.has_ac ? 'AC' : 'Non-AC'}
            </span>
          </div>

          <div class="space-y-2 pt-1">
            <p class="text-2xs uppercase font-extrabold text-slate-500 tracking-wider">Bed Occupancy</p>
            <div class="grid grid-cols-2 gap-2">
              ${bedsHtml}
            </div>
          </div>

          <div class="pt-3 border-t border-slate-200 text-2xs text-slate-500 flex items-center justify-between">
            <span class="truncate max-w-[200px] flex items-center gap-1 font-medium">
              <i data-lucide="sparkles" class="w-3 h-3 text-[#FFD200] shrink-0 fill-[#FFD200]"></i>
              ${room.amenities || 'Attached Bathroom, Wi-Fi, CCTV'}
            </span>
            <span class="font-extrabold ${vacantCount > 0 ? 'text-[#10A875]' : 'text-slate-400'}">${vacantCount} vacant</span>
          </div>
        </div>
      `;
    }).join('');

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Error loading rooms:', err);
  }
}

// ----------------------------------------------------
// 3. TENANTS TAB
// ----------------------------------------------------
async function loadTenants() {
  try {
    const search = document.getElementById('tenant-search')?.value.trim() || '';

    let url = `${API_BASE}/tenants?`;
    if (search) url += `search=${encodeURIComponent(search)}&`;

    const res = await fetch(url);
    const tenants = await res.json();
    state.tenants = tenants;
    renderTenantsList(tenants);
  } catch (err) {
    console.error('Error loading tenants:', err);
  }
}

function filterTenants() {
  const query = document.getElementById('tenant-search')?.value.toLowerCase().trim() || '';
  if (!query) {
    renderTenantsList(state.tenants);
    return;
  }
  const filtered = state.tenants.filter(t => 
    t.full_name.toLowerCase().includes(query) ||
    (t.phone && t.phone.includes(query)) ||
    (t.bed && t.bed.bed_number.toLowerCase().includes(query))
  );
  renderTenantsList(filtered);
}

function renderTenantsList(tenants) {
  const tbody = document.getElementById('tenants-tbody');
  if (!tbody) return;

  if (tenants.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center py-12 text-slate-500 text-xs">No matching residents found.</td></tr>`;
    return;
  }

  tbody.innerHTML = tenants.map(t => {
    const cleanPhone = t.phone ? t.phone.replace(/[^0-9]/g, '') : '';
    return `
      <tr class="hover:bg-blue-50/60 transition">
        <td class="px-6 py-4">
          <div class="font-extrabold text-[#062B63] text-sm">${t.full_name}</div>
          <div class="text-slate-500 text-2xs mt-0.5 flex items-center gap-2">
            <span>${t.phone}</span>
            ${t.occupation ? `&bull; <span>${t.occupation}</span>` : ''}
          </div>
        </td>
        <td class="px-6 py-4">
          <span class="px-3 py-1 rounded-lg bg-[#0B4F9C]/10 text-[#0B4F9C] border border-[#0B4F9C]/30 font-extrabold text-xs">
            ${t.bed ? t.bed.bed_number : 'Unassigned'}
          </span>
        </td>
        <td class="px-6 py-4 text-slate-600 font-medium">${t.check_in_date || 'N/A'}</td>
        <td class="px-6 py-4 text-[#062B63] font-black">₹${t.security_deposit ? t.security_deposit.toLocaleString('en-IN') : 0}</td>
        <td class="px-6 py-4">
          <span class="px-2.5 py-1 rounded-full text-2xs font-extrabold border ${t.kyc_status === 'VERIFIED' ? 'bg-[#10A875]/15 text-[#10A875] border-[#10A875]/30' : 'bg-[#F36C00]/15 text-[#F36C00] border-[#F36C00]/30'}">
            ${t.kyc_status}
          </span>
        </td>
        <td class="px-6 py-4 text-right">
          <div class="flex items-center justify-end gap-2">
            ${cleanPhone ? `
              <a href="https://api.whatsapp.com/send?phone=91${cleanPhone.slice(-10)}" target="_blank" class="p-2 rounded-xl bg-[#10A875]/15 hover:bg-[#10A875]/25 text-[#10A875] border border-[#10A875]/30 transition" title="WhatsApp Resident">
                <i data-lucide="message-circle" class="w-3.5 h-3.5"></i>
              </a>
              <a href="tel:${t.phone}" class="p-2 rounded-xl bg-[#0B4F9C]/15 hover:bg-[#0B4F9C]/25 text-[#0B4F9C] border border-[#0B4F9C]/30 transition" title="Call Resident">
                <i data-lucide="phone" class="w-3.5 h-3.5"></i>
              </a>
            ` : ''}
            ${t.is_active ? `
              <button onclick="checkoutTenant(${t.id}, '${t.full_name}')" class="px-3 py-1.5 rounded-xl border border-[#F21F26]/30 bg-[#F21F26]/10 hover:bg-[#F21F26]/20 text-[#F21F26] text-2xs font-bold transition">
                Check Out
              </button>
            ` : `<span class="text-slate-400 text-2xs italic">Checked Out</span>`}
          </div>
        </td>
      </tr>
    `;
  }).join('');

  if (window.lucide) lucide.createIcons();
}

// ----------------------------------------------------
// 4. BILLING & PAYMENTS TAB
// ----------------------------------------------------
async function loadBilling() {
  try {
    const [invRes, payRes] = await Promise.all([
      fetch(`${API_BASE}/billing/invoices`),
      fetch(`${API_BASE}/billing/payments`),
    ]);

    const invoices = await invRes.json();
    const payments = await payRes.json();
    state.invoices = invoices;
    state.payments = payments;

    // Invoices Table
    const invTbody = document.getElementById('invoices-tbody');
    if (invTbody) {
      if (invoices.length === 0) {
        invTbody.innerHTML = `<tr><td colspan="4" class="px-5 py-6 text-center text-slate-500 text-xs">No invoices generated yet.</td></tr>`;
      } else {
        invTbody.innerHTML = invoices.map(inv => {
          let statusBadge = 'bg-slate-100 text-slate-600 border-slate-200';
          if (inv.status === 'PAID') statusBadge = 'bg-[#10A875]/15 text-[#10A875] border-[#10A875]/30';
          else if (inv.status === 'PARTIAL') statusBadge = 'bg-[#F36C00]/15 text-[#F36C00] border-[#F36C00]/30';
          else if (inv.status === 'UNPAID') statusBadge = 'bg-[#F21F26]/15 text-[#F21F26] border-[#F21F26]/30';

          return `
            <tr class="hover:bg-blue-50/60 transition">
              <td class="px-5 py-3.5 font-mono text-2xs text-[#0B4F9C] font-extrabold">${inv.invoice_number}</td>
              <td class="px-5 py-3.5">
                <span class="font-bold text-[#062B63] text-xs block">${inv.tenant_name || ('Tenant #' + inv.tenant_id)}</span>
                <span class="text-2xs text-slate-500">${inv.billing_month}</span>
              </td>
              <td class="px-5 py-3.5 font-extrabold text-[#062B63] text-xs">₹${inv.total_amount.toLocaleString('en-IN')}</td>
              <td class="px-5 py-3.5">
                <span class="px-2.5 py-1 rounded-full text-2xs font-extrabold border ${statusBadge}">${inv.status}</span>
              </td>
            </tr>
          `;
        }).join('');
      }
    }

    // Payments Table
    const payTbody = document.getElementById('payments-tbody');
    if (payTbody) {
      if (payments.length === 0) {
        payTbody.innerHTML = `<tr><td colspan="4" class="px-5 py-6 text-center text-slate-500 text-xs">No payment records logged yet.</td></tr>`;
      } else {
        payTbody.innerHTML = payments.map(p => `
          <tr class="hover:bg-blue-50/60 transition">
            <td class="px-5 py-3.5 font-mono text-2xs text-[#5A18C9] font-extrabold">${p.receipt_number}</td>
            <td class="px-5 py-3.5">
              <span class="font-bold text-[#062B63] text-xs block">${p.tenant_name || ('Tenant #' + p.tenant_id)}</span>
              <span class="text-2xs text-slate-500">${p.payment_method} &bull; ${new Date(p.payment_date).toLocaleDateString()}</span>
            </td>
            <td class="px-5 py-3.5 font-extrabold text-[#10A875] text-xs">₹${p.amount.toLocaleString('en-IN')}</td>
            <td class="px-5 py-3.5 text-right">
              <button onclick="showPaymentReceipt(${p.id})" class="px-3 py-1.5 rounded-xl bg-[#062B63] hover:bg-[#0B4F9C] text-[#FFD200] font-black text-2xs inline-flex items-center gap-1.5 shadow-sm border border-[#FFD200]/40 transition transform hover:scale-105">
                <i data-lucide="receipt" class="w-3 h-3"></i> Receipt
              </button>
            </td>
          </tr>
        `).join('');
      }
    }

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Error loading billing:', err);
  }
}

// ----------------------------------------------------
// 5. MAINTENANCE TAB
// ----------------------------------------------------
async function loadComplaints() {
  try {
    const res = await fetch(`${API_BASE}/complaints`);
    const tickets = await res.json();
    state.tickets = tickets;

    const grid = document.getElementById('tickets-grid');
    if (!grid) return;

    if (tickets.length === 0) {
      grid.innerHTML = `<div class="col-span-3 text-center py-16 text-slate-500 text-xs">No service requests recorded. All facilities clear!</div>`;
      return;
    }

    grid.innerHTML = tickets.map(tk => {
      let statusColor = 'bg-slate-100 text-slate-600 border-slate-200';
      if (tk.status === 'RESOLVED' || tk.status === 'CLOSED') statusColor = 'bg-[#10A875]/15 text-[#10A875] border-[#10A875]/30';
      else if (tk.status === 'IN_PROGRESS') statusColor = 'bg-[#F36C00]/15 text-[#F36C00] border-[#F36C00]/30';
      else if (tk.status === 'OPEN') statusColor = 'bg-[#F21F26]/15 text-[#F21F26] border-[#F21F26]/30';

      return `
        <div class="brand-card rounded-2xl p-6 space-y-4 hover:-translate-y-1 transition-all duration-300">
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="flex items-center gap-2">
                <span class="font-mono text-2xs px-2 py-0.5 rounded-full bg-[#EAF3FA] text-[#062B63] border border-blue-200 font-extrabold">#${tk.ticket_number}</span>
                <span class="px-2.5 py-0.5 rounded-full text-2xs font-extrabold border ${statusColor}">${tk.status}</span>
              </div>
              <h4 class="font-extrabold text-[#062B63] text-base mt-2">${tk.title}</h4>
            </div>
            <span class="px-2.5 py-1 rounded-full text-2xs font-extrabold border shrink-0 ${tk.priority === 'URGENT' || tk.priority === 'HIGH' ? 'bg-[#F21F26]/15 text-[#F21F26] border-[#F21F26]/30' : 'bg-[#F36C00]/15 text-[#F36C00] border-[#F36C00]/30'}">
              ${tk.priority}
            </span>
          </div>

          <p class="text-xs text-slate-600 leading-relaxed">${tk.description || 'No description provided'}</p>
          ${tk.resolution_notes ? `<p class="text-2xs text-[#10A875] italic bg-[#10A875]/10 p-2.5 rounded-xl border border-[#10A875]/20 font-semibold">Resolution: ${tk.resolution_notes}</p>` : ''}

          <div class="pt-3 border-t border-slate-200 flex items-center justify-between">
            <span class="text-2xs text-slate-500 font-bold uppercase tracking-wider">${tk.category}</span>
            ${tk.status !== 'RESOLVED' && tk.status !== 'CLOSED' ? `
              <button onclick="resolveTicket(${tk.id})" class="px-3 py-1.5 rounded-xl bg-[#10A875] hover:bg-emerald-600 text-white text-xs font-bold shadow-sm transition">
                Mark Resolved
              </button>
            ` : `<span class="text-2xs text-[#10A875] font-extrabold flex items-center gap-1"><i data-lucide="check" class="w-3 h-3"></i> Completed</span>`}
          </div>
        </div>
      `;
    }).join('');

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Error loading complaints:', err);
  }
}

// ----------------------------------------------------
// 6. MESS & MEALS TAB
// ----------------------------------------------------
async function loadMeals() {
  try {
    const [menuRes, headcountRes] = await Promise.all([
      fetch(`${API_BASE}/meals/menu`),
      fetch(`${API_BASE}/meals/headcount?meal_type=DINNER`),
    ]);

    const menu = await menuRes.json();
    const headcount = await headcountRes.json();
    state.meals = menu;

    // Headcount widgets
    const hb = document.getElementById('headcount-breakfast');
    const hl = document.getElementById('headcount-lunch');
    const hd = document.getElementById('headcount-dinner');
    if (hb) hb.innerText = headcount.attending_count || 5;
    if (hl) hl.innerText = Math.max(1, (headcount.attending_count || 5) - 2);
    if (hd) hd.innerText = headcount.attending_count || 6;

    renderMealsForDay(state.selectedMealDay);
  } catch (err) {
    console.error('Error loading meals:', err);
  }
}

function switchMealDay(day) {
  state.selectedMealDay = day;

  // Update chip styles
  document.querySelectorAll('#meal-days-chips button').forEach(btn => {
    if (btn.getAttribute('data-day') === day) {
      btn.className = 'px-4 py-2 rounded-xl text-xs font-bold bg-[#062B63] text-white border border-[#FFD200] shadow-md shrink-0';
    } else {
      btn.className = 'px-4 py-2 rounded-xl text-xs font-semibold bg-white text-slate-700 hover:bg-blue-50 border border-slate-200 shrink-0';
    }
  });

  renderMealsForDay(day);
}

function renderMealsForDay(day) {
  const grid = document.getElementById('meals-cards-grid');
  if (!grid) return;

  const dayItems = state.meals.filter(m => m.day_of_week === day);

  const getMenuFor = (type, fallback) => {
    const found = dayItems.find(m => m.meal_type === type);
    return found ? found.items_description : fallback;
  };

  const breakfastText = getMenuFor('BREAKFAST', 'Idli, Vada, Hot Sambar, Coconut Chutney, Fresh Tea & Coffee');
  const lunchText = getMenuFor('LUNCH', 'Steamed Rice, South Indian Dal / Rasam, Seasonal Veg Curry, Curd, Papad');
  const dinnerText = getMenuFor('DINNER', 'Fresh Chapati / Roti, Paneer / Mixed Veg Curry, Flavored Rice, Curd');

  grid.innerHTML = `
    <!-- Breakfast -->
    <div class="brand-card rounded-2xl p-6 space-y-4 hover:-translate-y-1 transition-all duration-300">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-[#FFD200]/25 text-[#062B63] flex items-center justify-center font-bold">
            <i data-lucide="sunrise" class="w-5 h-5"></i>
          </div>
          <div>
            <h4 class="font-black text-[#062B63] text-base">Breakfast</h4>
            <span class="text-2xs text-slate-500 font-semibold">7:30 AM - 9:30 AM</span>
          </div>
        </div>
        <span class="px-2.5 py-0.5 rounded-full bg-[#FFD200]/30 text-[#062B63] text-2xs font-extrabold border border-[#FFD200]">Morning</span>
      </div>
      <p class="text-xs text-slate-800 leading-relaxed font-semibold bg-[#EAF3FA] p-4 rounded-xl border border-blue-200">${breakfastText}</p>
    </div>

    <!-- Lunch -->
    <div class="brand-card rounded-2xl p-6 space-y-4 hover:-translate-y-1 transition-all duration-300">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-[#5A18C9]/15 text-[#5A18C9] flex items-center justify-center font-bold">
            <i data-lucide="sun" class="w-5 h-5"></i>
          </div>
          <div>
            <h4 class="font-black text-[#062B63] text-base">Lunch</h4>
            <span class="text-2xs text-slate-500 font-semibold">12:30 PM - 2:30 PM</span>
          </div>
        </div>
        <span class="px-2.5 py-0.5 rounded-full bg-[#5A18C9]/15 text-[#5A18C9] text-2xs font-extrabold border border-[#5A18C9]/30">Afternoon</span>
      </div>
      <p class="text-xs text-slate-800 leading-relaxed font-semibold bg-[#EAF3FA] p-4 rounded-xl border border-blue-200">${lunchText}</p>
    </div>

    <!-- Dinner -->
    <div class="brand-card rounded-2xl p-6 space-y-4 hover:-translate-y-1 transition-all duration-300">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl bg-[#062B63]/15 text-[#062B63] flex items-center justify-center font-bold">
            <i data-lucide="moon" class="w-5 h-5"></i>
          </div>
          <div>
            <h4 class="font-black text-[#062B63] text-base">Dinner</h4>
            <span class="text-2xs text-slate-500 font-semibold">7:30 PM - 9:45 PM</span>
          </div>
        </div>
        <span class="px-2.5 py-0.5 rounded-full bg-[#062B63]/15 text-[#062B63] text-2xs font-extrabold border border-[#062B63]/30">Night</span>
      </div>
      <p class="text-xs text-slate-800 leading-relaxed font-semibold bg-[#EAF3FA] p-4 rounded-xl border border-blue-200">${dinnerText}</p>
    </div>
  `;

  if (window.lucide) lucide.createIcons();
}

// ----------------------------------------------------
// HELPER: POPULATE MODAL DROPDOWNS
// ----------------------------------------------------
async function loadAvailableBedsDropdown() {
  const select = document.getElementById('onboard-bed-select');
  if (!select) return;
  select.innerHTML = '<option value="">Loading available beds...</option>';
  try {
    const res = await fetch(`${API_BASE}/rooms/beds/available`);
    const beds = await res.json();
    if (beds.length === 0) {
      select.innerHTML = '<option value="">No vacant beds! Create a room first.</option>';
      return;
    }
    select.innerHTML = beds.map(b => `<option value="${b.id}">Bed ${b.bed_number} (Room ID ${b.room_id})</option>`).join('');
  } catch (err) {
    select.innerHTML = '<option value="">Failed to load beds</option>';
  }
}

async function loadTenantsDropdown() {
  const selects = [
    document.getElementById('payment-tenant-select'), 
    document.getElementById('invoice-tenant-select'),
    document.getElementById('attendance-tenant-select')
  ];
  try {
    const res = await fetch(`${API_BASE}/tenants?is_active=true`);
    const tenants = await res.json();
    const options = '<option value="">-- Choose Resident --</option>' + 
      tenants.map(t => `<option value="${t.id}">${t.full_name} (${t.bed ? t.bed.bed_number : 'No Bed'})</option>`).join('');
    selects.forEach(s => { if (s) s.innerHTML = options; });
  } catch (err) {
    console.error(err);
  }
}

function updatePaymentAmountSuggestion(tenantId) {
  const amountInput = document.getElementById('payment-amount');
  if (!amountInput || !tenantId) return;
  const t = state.tenants.find(item => item.id == tenantId);
  if (t && t.monthly_rent) {
    amountInput.value = t.monthly_rent;
  }
}

// ----------------------------------------------------
// FORM ACTIONS & API MUTATIONS
// ----------------------------------------------------
async function handleOnboardTenant(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const payload = {
    full_name: formData.get('name'),
    phone: formData.get('phone'),
    email: null,
    occupation: null,
    id_proof_type: 'AADHAAR',
    id_proof_number: null,
    bed_id: parseInt(formData.get('bed_id')),
    security_deposit: parseFloat(formData.get('deposit_amount') || 0),
    monthly_rent: parseFloat(formData.get('monthly_rent') || 6500),
    check_in_date: formData.get('check_in_date'),
    emergency_contact: formData.get('emergency_contact') || null,
  };

  try {
    const res = await fetch(`${API_BASE}/tenants/onboard`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to onboard tenant');
    }
    closeModal('modal-onboard');
    form.reset();
    showToast('Tenant onboarded and bed locked successfully!');
    refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function handleAddRoom(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const payload = {
    room_number: formData.get('room_number'),
    floor: parseInt(formData.get('floor')),
    room_type: formData.get('room_type'),
    base_rent: parseFloat(formData.get('base_rent')),
    has_ac: form.querySelector('input[name="has_ac"]').checked,
    has_attached_bathroom: form.querySelector('input[name="has_attached_bathroom"]').checked,
    amenities: 'Attached Bathroom, High-Speed Wi-Fi, 24/7 CCTV, Washing Machine',
  };

  try {
    const res = await fetch(`${API_BASE}/rooms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create room');
    }
    closeModal('modal-room');
    form.reset();
    showToast('Room and beds created successfully!');
    refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

let currentReceiptData = null;

async function handleRecordPayment(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const tenantIdStr = formData.get('tenant_id');
  const amountStr = formData.get('amount');

  if (!tenantIdStr) {
    showToast('Please select a tenant.', 'error');
    return;
  }
  const tenantId = parseInt(tenantIdStr);
  const amount = parseFloat(amountStr);

  if (isNaN(amount) || amount <= 0) {
    showToast('Please enter a valid payment amount.', 'error');
    return;
  }

  const payload = {
    tenant_id: tenantId,
    amount: amount,
    payment_method: formData.get('payment_mode'),
    transaction_reference: formData.get('transaction_ref') || null,
    notes: 'Rent & Maintenance Payment',
  };

  try {
    const res = await fetch(`${API_BASE}/billing/payments`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      let msg = 'Failed to record payment';
      if (typeof err.detail === 'string') msg = err.detail;
      throw new Error(msg);
    }
    const savedPayment = await res.json();
    closeModal('modal-payment');
    form.reset();
    showToast('Payment recorded! Generating receipt...');
    await refreshAllData();
    showPaymentReceipt(savedPayment.id);
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function showPaymentReceipt(paymentId) {
  try {
    const res = await fetch(`${API_BASE}/billing/payments/${paymentId}/receipt`);
    if (!res.ok) throw new Error('Could not fetch receipt details');
    const data = await res.json();
    currentReceiptData = data;

    const setVal = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.innerText = val;
    };

    setVal('rcpt-number', data.receipt_number || 'RCP-0000');
    setVal('rcpt-date', data.payment_date || 'Today');
    setVal('rcpt-tenant-name', data.tenant_name || 'Guest');
    setVal('rcpt-bed', data.bed_number ? `Bed: ${data.bed_number}` : 'N/A');
    setVal('rcpt-mode', data.payment_method || 'UPI');
    setVal('rcpt-amount', `₹${data.amount ? data.amount.toLocaleString('en-IN') : 0}`);
    setVal('rcpt-ref', `Ref: ${data.transaction_reference || 'UPI/Cash'}`);

    openModal('modal-view-receipt');
  } catch (err) {
    showToast(err.message || 'Error generating receipt', 'error');
  }
}

function downloadReceiptPDF() {
  if (!currentReceiptData || !currentReceiptData.payment_id) {
    showToast('No receipt loaded to download.', 'error');
    return;
  }
  showToast('Downloading official PDF receipt...', 'info');
  const paymentId = currentReceiptData.payment_id;
  const downloadUrl = `${API_BASE}/billing/payments/${paymentId}/download-pdf`;

  // Direct download link trigger (universal for phones & PCs)
  const a = document.createElement('a');
  a.href = downloadUrl;
  a.setAttribute('download', `Latha_PG_Receipt_${currentReceiptData.receipt_number || 'REC'}.pdf`);
  a.setAttribute('target', '_blank');
  document.body.appendChild(a);
  a.click();
  setTimeout(() => {
    if (a.parentNode) a.parentNode.removeChild(a);
  }, 1000);
}

function shareReceiptOnWhatsApp() {
  if (!currentReceiptData) {
    showToast('No receipt selected.', 'error');
    return;
  }
  const d = currentReceiptData;
  const origin = window.location.origin;
  const pdfLink = `${origin}${API_BASE}/billing/payments/${d.payment_id}/download-pdf`;

  const text = `*LATHA PG FOR GENTS - PAYMENT RECEIPT*\n` +
    `━━━━━━━━━━━━━━━━━━━━\n` +
    `📋 *Receipt No:* ${d.receipt_number}\n` +
    `📅 *Date:* ${d.payment_date}\n` +
    `👤 *Tenant:* ${d.tenant_name}\n` +
    `🛏️ *Bed:* ${d.bed_number || 'Standard'}\n` +
    `💰 *Amount Paid:* ₹${d.amount ? d.amount.toLocaleString('en-IN') : 0}\n` +
    `💳 *Payment Mode:* ${d.payment_method} (${d.transaction_reference || 'Ref: Verified'})\n` +
    `━━━━━━━━━━━━━━━━━━━━\n` +
    `📄 *Download Official PDF Receipt:*\n` +
    `${pdfLink}\n` +
    `━━━━━━━━━━━━━━━━━━━━\n` +
    `Thank you for staying at Latha PG!\n` +
    `🏢 Latha PG for Gents (ಲತಾ ಪಿಜಿ)\n` +
    `📞 Helplines: 9353439703 / 9019870803`;

  const rawPhone = d.tenant_phone && d.tenant_phone !== 'N/A' ? d.tenant_phone.replace(/[^0-9]/g, '') : '';
  
  let waUrl = '';
  if (rawPhone.length >= 10) {
    waUrl = `https://wa.me/91${rawPhone.slice(-10)}?text=${encodeURIComponent(text)}`;
  } else {
    waUrl = `https://wa.me/?text=${encodeURIComponent(text)}`;
  }

  // Open WhatsApp directly without popup blocker
  showToast('Opening WhatsApp...', 'info');
  window.location.href = waUrl;
}

async function shareReceiptNative() {
  if (!currentReceiptData) return;
  const d = currentReceiptData;
  const origin = window.location.origin;
  const pdfLink = `${origin}${API_BASE}/billing/payments/${d.payment_id}/download-pdf`;

  const shareText = `*Latha PG Rent Receipt*\n` +
    `Receipt: ${d.receipt_number}\n` +
    `Tenant: ${d.tenant_name}\n` +
    `Amount: ₹${d.amount ? d.amount.toLocaleString('en-IN') : 0}\n` +
    `Download PDF: ${pdfLink}\n` +
    `Helplines: 9353439703 / 9019870803`;

  if (navigator.share) {
    try {
      await navigator.share({
        title: `Latha PG Receipt - ${d.receipt_number}`,
        text: shareText,
        url: pdfLink
      });
      showToast('Shared successfully!');
    } catch (err) {
      if (err.name !== 'AbortError') {
        shareReceiptOnWhatsApp();
      }
    }
  } else {
    shareReceiptOnWhatsApp();
  }
}

async function handleCreateInvoice(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const payload = {
    tenant_id: parseInt(formData.get('tenant_id')),
    billing_month: formData.get('billing_month'),
    due_date: formData.get('due_date'),
    rent_amount: parseFloat(formData.get('rent_amount')),
    utility_charges: 0,
  };

  try {
    const res = await fetch(`${API_BASE}/billing/invoices`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to issue invoice');
    }
    closeModal('modal-invoice');
    form.reset();
    showToast('Rent invoice generated successfully!');
    refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}
const handleGenerateInvoice = handleCreateInvoice;

async function handleCreateTicket(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const payload = {
    title: formData.get('title'),
    category: formData.get('category'),
    priority: formData.get('priority'),
    description: formData.get('description'),
  };

  try {
    const res = await fetch(`${API_BASE}/complaints`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to submit service ticket');
    }
    closeModal('modal-ticket');
    form.reset();
    showToast('Maintenance ticket reported successfully!');
    refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}
const handleRaiseComplaint = handleCreateTicket;

async function handleUpdateMealMenu(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const payload = {
    day_of_week: formData.get('day_of_week'),
    meal_type: formData.get('meal_type'),
    items_description: formData.get('items_description'),
  };

  try {
    const res = await fetch(`${API_BASE}/meals/menu`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to update meal menu');
    closeModal('modal-meal-menu');
    form.reset();
    showToast('Meal menu updated successfully!');
    refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function handleMarkAttendance(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const payload = {
    tenant_id: parseInt(formData.get('tenant_id')),
    date: new Date().toISOString().split('T')[0],
    meal_type: formData.get('meal_type'),
    is_attending: formData.get('is_attending') === 'true',
    wants_packed_meal: false,
    feedback: null,
  };

  try {
    const res = await fetch(`${API_BASE}/meals/attendance`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to mark meal attendance');
    closeModal('modal-attendance');
    form.reset();
    showToast('Kitchen attendance headcount recorded!');
    refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function checkoutTenant(tenantId, name) {
  if (!confirm(`Are you sure you want to check out ${name}? This will mark their bed as AVAILABLE immediately.`)) return;
  try {
    const res = await fetch(`${API_BASE}/tenants/${tenantId}/checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    if (!res.ok) throw new Error('Checkout failed');
    showToast(`${name} checked out. Bed is now vacant!`);
    refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function resolveTicket(ticketId) {
  const notes = prompt('Enter resolution notes:', 'Repaired and verified');
  if (notes === null) return;
  try {
    const res = await fetch(`${API_BASE}/complaints/${ticketId}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'RESOLVED', resolution_notes: notes }),
    });
    if (!res.ok) throw new Error('Failed to resolve ticket');
    showToast('Ticket marked as resolved!');
    refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

// Mobile Sidebar Drawer Toggle
function toggleSidebar(show) {
  const sidebar = document.getElementById('sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');
  if (!sidebar) return;
  if (show === undefined) {
    sidebar.classList.toggle('-translate-x-full');
    if (backdrop) backdrop.classList.toggle('hidden');
  } else if (show) {
    sidebar.classList.remove('-translate-x-full');
    if (backdrop) backdrop.classList.remove('hidden');
  } else {
    sidebar.classList.add('-translate-x-full');
    if (backdrop) backdrop.classList.add('hidden');
  }
}

// PWA Installation Handling
let deferredPrompt = null;
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const pwaBtn = document.getElementById('pwa-install-btn');
  if (pwaBtn) pwaBtn.style.display = 'inline-flex';
});

function triggerPwaInstall() {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        showToast('Thank you! Latha PG app is installing.', 'success');
      }
      deferredPrompt = null;
      const pwaBtn = document.getElementById('pwa-install-btn');
      if (pwaBtn) pwaBtn.style.display = 'none';
    });
  } else {
    showToast('To install: tap your browser menu (⋮) and select "Add to Home screen" or "Install App".', 'info');
  }
}

// Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/dashboard/sw.js')
      .then((reg) => console.log('PWA Service Worker registered:', reg.scope))
      .catch((err) => console.warn('PWA Service Worker registration failed:', err));
  });
}

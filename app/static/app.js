// PG Manager Pro - Frontend Controller

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
  summary: null,
};

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
  switchTab('overview');
  refreshAllData();
});

// Toast notification helper
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  const bgColor = type === 'success' ? 'bg-emerald-600' : type === 'error' ? 'bg-rose-600' : 'bg-slate-800';
  
  toast.className = `${bgColor} text-white px-4 py-2.5 rounded-lg shadow-lg text-xs flex items-center gap-2 transform transition duration-300 translate-y-2 opacity-0`;
  toast.innerHTML = `<span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => {
    toast.classList.remove('translate-y-2', 'opacity-0');
  }, 10);

  setTimeout(() => {
    toast.classList.add('opacity-0');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Tab Switching
function switchTab(tabName) {
  state.activeTab = tabName;

  // Update nav buttons (desktop sidebar)
  document.querySelectorAll('[data-tab-btn]').forEach(btn => {
    if (btn.getAttribute('data-tab-btn') === tabName) {
      btn.className = 'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg transition text-left active bg-blue-600 text-white shadow-sm';
    } else {
      btn.className = 'w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg transition text-left hover:bg-slate-800 text-slate-300';
    }
  });

  // Update mobile bottom nav buttons
  document.querySelectorAll('[data-mobile-tab]').forEach(btn => {
    if (btn.getAttribute('data-mobile-tab') === tabName) {
      btn.className = 'flex flex-col items-center justify-center flex-1 py-1 text-amber-400 font-medium transition';
    } else {
      btn.className = 'flex flex-col items-center justify-center flex-1 py-1 text-slate-400 hover:text-slate-200 transition';
    }
  });

  // Auto-close mobile drawer
  if (typeof toggleSidebar === 'function') toggleSidebar(false);

  // Update content visibility
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
  });
  const targetTab = document.getElementById(`tab-${tabName}`);
  if (targetTab) targetTab.classList.add('active');

  // Page titles
  const titles = {
    overview: ['Executive Overview', 'Live occupancy, revenue, and PG operations'],
    rooms: ['Rooms & Bed Allocations', 'Visual occupancy map and sharing capacity'],
    tenants: ['Tenants & KYC Directory', 'Active guests, KYC documents, and check-ins'],
    billing: ['Billing, Rent & Receipts', 'Monthly invoices, payments, and balance tracking'],
    complaints: ['Maintenance & Tickets', 'Track repairs, complaints, and service requests'],
    meals: ['Mess & Meal Schedule', 'Weekly food menu and kitchen attendance headcount'],
  };

  if (titles[tabName]) {
    document.getElementById('page-title').innerText = titles[tabName][0];
    document.getElementById('page-subtitle').innerText = titles[tabName][1];
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

  // Populate dynamic dropdowns
  if (id === 'modal-onboard') loadAvailableBedsDropdown();
  if (id === 'modal-payment' || id === 'modal-invoice') loadTenantsDropdown();
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
    document.getElementById('stat-occupancy-rate').innerText = `${data.occupancy_rate_percent}%`;
    document.getElementById('stat-occupied-beds').innerText = `${data.occupied_beds}/${data.total_beds} beds`;
    document.getElementById('stat-occupancy-bar').style.width = `${data.occupancy_rate_percent}%`;
    document.getElementById('stat-available-beds').innerText = data.available_beds;
    document.getElementById('stat-collected').innerText = `₹${data.total_collected_amount.toLocaleString('en-IN')}`;
    document.getElementById('stat-billed').innerText = `Total Billed: ₹${data.total_billed_amount.toLocaleString('en-IN')}`;
    document.getElementById('stat-dues').innerText = `₹${data.total_outstanding_dues.toLocaleString('en-IN')}`;

    // Recent checked-in tenants
    const tenantsRes = await fetch(`${API_BASE}/tenants?is_active=true`);
    const tenants = await tenantsRes.json();
    const tbody = document.getElementById('overview-tenants-tbody');
    tbody.innerHTML = tenants.slice(0, 5).map(t => `
      <tr class="hover:bg-slate-50 transition">
        <td class="px-6 py-3 font-medium text-slate-900">${t.full_name}</td>
        <td class="px-6 py-3"><span class="px-2 py-0.5 rounded bg-blue-50 text-blue-700 font-semibold text-2xs">${t.bed ? t.bed.bed_number : 'Unassigned'}</span></td>
        <td class="px-6 py-3 text-slate-500">${t.phone}</td>
        <td class="px-6 py-3">
          <span class="px-2 py-0.5 rounded-full text-2xs font-semibold ${t.kyc_status === 'VERIFIED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">
            ${t.kyc_status}
          </span>
        </td>
      </tr>
    `).join('');

    // Urgent Tickets
    const ticketsRes = await fetch(`${API_BASE}/complaints?status=OPEN`);
    const tickets = await ticketsRes.json();
    const ticketsContainer = document.getElementById('overview-tickets-list');
    if (tickets.length === 0) {
      ticketsContainer.innerHTML = `<p class="text-xs text-slate-400 py-2">No pending maintenance alerts.</p>`;
    } else {
      ticketsContainer.innerHTML = tickets.slice(0, 3).map(tk => `
        <div class="p-3 rounded-lg border border-slate-100 bg-slate-50/50 flex items-start justify-between">
          <div>
            <p class="font-medium text-slate-900 text-xs">${tk.title}</p>
            <p class="text-slate-500 text-2xs mt-0.5">${tk.category} &bull; Ticket #${tk.ticket_number}</p>
          </div>
          <span class="px-1.5 py-0.5 rounded text-2xs font-bold ${tk.priority === 'URGENT' || tk.priority === 'HIGH' ? 'bg-rose-100 text-rose-700' : 'bg-amber-100 text-amber-700'}">${tk.priority}</span>
        </div>
      `).join('');
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
    const acFilter = document.getElementById('filter-room-ac').value;
    const floorFilter = document.getElementById('filter-room-floor').value;

    let url = `${API_BASE}/rooms?`;
    if (acFilter) url += `has_ac=${acFilter}&`;
    if (floorFilter) url += `floor=${floorFilter}&`;

    const res = await fetch(url);
    const rooms = await res.json();
    state.rooms = rooms;

    const grid = document.getElementById('rooms-grid');
    if (rooms.length === 0) {
      grid.innerHTML = `<div class="col-span-3 text-center py-12 text-slate-400 text-xs">No rooms found. Click "+ Add Room" to create one.</div>`;
      return;
    }

    grid.innerHTML = rooms.map(room => {
      const bedsHtml = room.beds.map(bed => {
        let badgeColor = 'bg-emerald-50 border-emerald-300 text-emerald-800';
        let dotColor = 'bg-emerald-500';
        if (bed.status === 'OCCUPIED') {
          badgeColor = 'bg-blue-50 border-blue-300 text-blue-800';
          dotColor = 'bg-blue-600';
        } else if (bed.status === 'MAINTENANCE') {
          badgeColor = 'bg-amber-50 border-amber-300 text-amber-800';
          dotColor = 'bg-amber-500';
        }

        return `
          <div class="px-2.5 py-1.5 rounded-lg border ${badgeColor} flex items-center justify-between text-xs font-medium">
            <span class="flex items-center gap-1.5">
              <span class="w-2 h-2 rounded-full ${dotColor}"></span>
              ${bed.bed_number}
            </span>
            <span class="text-2xs uppercase tracking-wider font-semibold">${bed.status}</span>
          </div>
        `;
      }).join('');

      return `
        <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4 hover:shadow-md transition">
          <div class="flex items-start justify-between">
            <div>
              <div class="flex items-center gap-2">
                <h4 class="text-base font-bold text-slate-900">Room ${room.room_number}</h4>
                <span class="text-xs text-slate-400">Floor ${room.floor}</span>
              </div>
              <p class="text-xs text-slate-500 mt-0.5">${room.room_type} Sharing &bull; ₹${room.base_rent.toLocaleString('en-IN')}/bed</p>
            </div>
            <span class="px-2 py-0.5 rounded text-2xs font-semibold ${room.has_ac ? 'bg-sky-100 text-sky-800' : 'bg-slate-100 text-slate-600'}">
              ${room.has_ac ? 'AC' : 'Non-AC'}
            </span>
          </div>

          <div class="space-y-2">
            <p class="text-2xs uppercase font-semibold text-slate-400 tracking-wider">Bed Occupancy</p>
            <div class="grid grid-cols-2 gap-2">
              ${bedsHtml}
            </div>
          </div>

          <div class="pt-3 border-t border-slate-100 text-2xs text-slate-400 flex items-center justify-between">
            <span class="truncate max-w-[200px]">${room.amenities || 'Standard amenities'}</span>
            <span class="font-medium text-slate-600">${room.beds.filter(b => b.status === 'AVAILABLE').length} vacant</span>
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
    const search = document.getElementById('search-tenant').value.trim();
    const kyc = document.getElementById('filter-tenant-kyc').value;

    let url = `${API_BASE}/tenants?`;
    if (search) url += `search=${encodeURIComponent(search)}&`;
    if (kyc) url += `kyc_status=${kyc}&`;

    const res = await fetch(url);
    const tenants = await res.json();
    state.tenants = tenants;

    const tbody = document.getElementById('tenants-tbody');
    if (tenants.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-slate-400 text-xs">No tenants found.</td></tr>`;
      return;
    }

    tbody.innerHTML = tenants.map(t => `
      <tr class="hover:bg-slate-50 transition">
        <td class="px-6 py-4">
          <div class="font-semibold text-slate-900">${t.full_name}</div>
          <div class="text-slate-400 text-2xs">${t.phone} &bull; ${t.email || 'No email'}</div>
        </td>
        <td class="px-6 py-4">
          <span class="px-2.5 py-1 rounded-md bg-blue-50 text-blue-700 font-semibold text-xs">
            ${t.bed ? t.bed.bed_number : 'Unassigned'}
          </span>
        </td>
        <td class="px-6 py-4 text-slate-600">${t.occupation || 'N/A'}</td>
        <td class="px-6 py-4">
          <span class="px-2.5 py-1 rounded-full text-2xs font-semibold ${t.kyc_status === 'VERIFIED' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'}">
            ${t.kyc_status}
          </span>
        </td>
        <td class="px-6 py-4 text-slate-600">₹${t.security_deposit.toLocaleString('en-IN')}</td>
        <td class="px-6 py-4 text-slate-500">${t.check_in_date}</td>
        <td class="px-6 py-4 text-right">
          ${t.is_active ? `
            <button onclick="checkoutTenant(${t.id}, '${t.full_name}')" class="px-2.5 py-1 rounded border border-rose-200 text-rose-600 hover:bg-rose-50 text-2xs font-medium transition">
              Check Out
            </button>
          ` : `<span class="text-slate-400 text-2xs italic">Checked Out</span>`}
        </td>
      </tr>
    `).join('');

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Error loading tenants:', err);
  }
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
    invTbody.innerHTML = invoices.map(inv => {
      let statusBadge = 'bg-slate-100 text-slate-700';
      if (inv.status === 'PAID') statusBadge = 'bg-emerald-100 text-emerald-800';
      else if (inv.status === 'PARTIAL') statusBadge = 'bg-amber-100 text-amber-800';
      else if (inv.status === 'UNPAID') statusBadge = 'bg-rose-100 text-rose-800';

      return `
        <tr class="hover:bg-slate-50 transition">
          <td class="px-6 py-3.5 font-mono text-2xs font-medium text-slate-900">${inv.invoice_number}</td>
          <td class="px-6 py-3.5 text-slate-600">Tenant #${inv.tenant_id}</td>
          <td class="px-6 py-3.5 text-slate-600">${inv.billing_month}</td>
          <td class="px-6 py-3.5 font-semibold text-slate-900">₹${inv.total_amount.toLocaleString('en-IN')}</td>
          <td class="px-6 py-3.5 text-emerald-600">₹${inv.paid_amount.toLocaleString('en-IN')}</td>
          <td class="px-6 py-3.5 text-slate-500">${inv.due_date}</td>
          <td class="px-6 py-3.5">
            <span class="px-2 py-0.5 rounded-full text-2xs font-semibold ${statusBadge}">${inv.status}</span>
          </td>
        </tr>
      `;
    }).join('');

    // Payments Table
    const payTbody = document.getElementById('payments-tbody');
    payTbody.innerHTML = payments.map(p => `
      <tr class="hover:bg-slate-50 transition">
        <td class="px-6 py-3.5 font-mono text-2xs font-medium text-slate-900">${p.receipt_number}</td>
        <td class="px-6 py-3.5">
          <span class="font-semibold text-slate-900">${p.tenant_name || ('Tenant #' + p.tenant_id)}</span>
          <span class="text-2xs text-slate-400 block">${p.bed_number ? 'Bed ' + p.bed_number : ''}</span>
        </td>
        <td class="px-6 py-3.5 font-bold text-emerald-600">₹${p.amount.toLocaleString('en-IN')}</td>
        <td class="px-6 py-3.5"><span class="px-2 py-0.5 rounded bg-slate-100 text-slate-700 text-2xs font-semibold">${p.payment_method}</span></td>
        <td class="px-6 py-3.5 text-slate-400 text-2xs font-mono">${p.transaction_reference || 'N/A'}</td>
        <td class="px-6 py-3.5 text-slate-500">${new Date(p.payment_date).toLocaleDateString()}</td>
        <td class="px-6 py-3.5 text-right">
          <button onclick="showPaymentReceipt(${p.id})" class="px-2.5 py-1 rounded bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-2xs inline-flex items-center gap-1 shadow-sm transition">
            <i data-lucide="receipt" class="w-3 h-3"></i> View Receipt
          </button>
        </td>
      </tr>
    `).join('');

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Error loading billing:', err);
  }
}

// ----------------------------------------------------
// 5. COMPLAINTS TAB
// ----------------------------------------------------
async function loadComplaints() {
  try {
    const res = await fetch(`${API_BASE}/complaints`);
    const tickets = await res.json();
    state.tickets = tickets;

    const container = document.getElementById('tickets-container');
    if (tickets.length === 0) {
      container.innerHTML = `<div class="text-center py-12 text-slate-400 text-xs">No maintenance tickets reported.</div>`;
      return;
    }

    container.innerHTML = tickets.map(tk => {
      let statusColor = 'bg-slate-100 text-slate-700';
      if (tk.status === 'RESOLVED' || tk.status === 'CLOSED') statusColor = 'bg-emerald-100 text-emerald-800';
      else if (tk.status === 'IN_PROGRESS') statusColor = 'bg-amber-100 text-amber-800';
      else if (tk.status === 'OPEN') statusColor = 'bg-rose-100 text-rose-800';

      return `
        <div class="bg-white rounded-xl border border-slate-200 p-5 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div class="space-y-1">
            <div class="flex items-center gap-2">
              <span class="font-mono text-2xs px-2 py-0.5 rounded bg-slate-100 text-slate-600">${tk.ticket_number}</span>
              <span class="px-2 py-0.5 rounded-full text-2xs font-bold ${statusColor}">${tk.status}</span>
              <span class="text-2xs font-medium text-slate-400">${tk.category}</span>
            </div>
            <h4 class="font-semibold text-slate-900 text-sm">${tk.title}</h4>
            <p class="text-xs text-slate-600">${tk.description}</p>
            ${tk.resolution_notes ? `<p class="text-2xs text-emerald-700 mt-1 italic">Resolution: ${tk.resolution_notes}</p>` : ''}
          </div>

          <div class="flex items-center gap-3 shrink-0">
            <span class="px-2 py-1 rounded text-2xs font-bold ${tk.priority === 'URGENT' ? 'bg-rose-100 text-rose-700' : 'bg-slate-100 text-slate-700'}">
              ${tk.priority} Priority
            </span>
            ${tk.status !== 'RESOLVED' && tk.status !== 'CLOSED' ? `
              <button onclick="resolveTicket(${tk.id})" class="px-3 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-medium shadow-sm transition">
                Mark Resolved
              </button>
            ` : ''}
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

    // Headcount
    document.getElementById('headcount-attending').innerText = headcount.attending_count;
    document.getElementById('headcount-packed').innerText = headcount.packed_meal_count;
    document.getElementById('headcount-optout').innerText = headcount.opt_out_count;

    // Group menu by day
    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const grouped = {};
    days.forEach(d => { grouped[d] = { BREAKFAST: '-', LUNCH: '-', DINNER: '-' }; });

    menu.forEach(item => {
      if (grouped[item.day_of_week]) {
        grouped[item.day_of_week][item.meal_type] = item.items;
      }
    });

    const tbody = document.getElementById('meals-tbody');
    tbody.innerHTML = days.map(d => `
      <tr class="hover:bg-slate-50 transition">
        <td class="px-6 py-4 font-bold text-slate-900">${d}</td>
        <td class="px-6 py-4 text-slate-700">${grouped[d].BREAKFAST}</td>
        <td class="px-6 py-4 text-slate-700">${grouped[d].LUNCH}</td>
        <td class="px-6 py-4 text-slate-700">${grouped[d].DINNER}</td>
      </tr>
    `).join('');

    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error('Error loading meals:', err);
  }
}

// ----------------------------------------------------
// HELPER: POPULATE MODAL DROPDOWNS
// ----------------------------------------------------
async function loadAvailableBedsDropdown() {
  const select = document.getElementById('onboard-bed-select');
  select.innerHTML = '<option value="">Loading available beds...</option>';
  try {
    const res = await fetch(`${API_BASE}/rooms/beds/available`);
    const beds = await res.json();
    if (beds.length === 0) {
      select.innerHTML = '<option value="">No beds available! Add a room first.</option>';
      return;
    }
    select.innerHTML = beds.map(b => `<option value="${b.id}">Bed ${b.bed_number} (Room ID ${b.room_id})</option>`).join('');
  } catch (err) {
    select.innerHTML = '<option value="">Failed to load beds</option>';
  }
}

async function loadTenantsDropdown() {
  const selects = [document.getElementById('payment-tenant-select'), document.getElementById('invoice-tenant-select')];
  try {
    const res = await fetch(`${API_BASE}/tenants?is_active=true`);
    const tenants = await res.json();
    const options = tenants.map(t => `<option value="${t.id}">${t.full_name} (${t.bed ? t.bed.bed_number : 'No Bed'})</option>`).join('');
    selects.forEach(s => { if (s) s.innerHTML = options; });
  } catch (err) {
    console.error(err);
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
    full_name: formData.get('full_name'),
    phone: formData.get('phone'),
    email: formData.get('email') || null,
    occupation: formData.get('occupation') || null,
    id_proof_type: formData.get('id_proof_type'),
    id_proof_number: formData.get('id_proof_number') || null,
    bed_id: parseInt(formData.get('bed_id')),
    security_deposit: parseFloat(formData.get('security_deposit') || 0),
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
    amenities: formData.get('amenities'),
  };

  try {
    const res = await fetch(`${API_BASE}/rooms`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to add room');
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
    payment_method: formData.get('payment_method'),
    transaction_reference: formData.get('transaction_reference') || null,
    notes: formData.get('notes') || null,
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
      else if (Array.isArray(err.detail) && err.detail.length > 0) msg = err.detail[0].msg;
      throw new Error(msg);
    }
    const savedPayment = await res.json();
    closeModal('modal-payment');
    form.reset();
    showToast('Payment recorded successfully! Generating receipt...');
    await refreshAllData();
    // Instantly pop up the official printable receipt!
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

    document.getElementById('rcpt-number').innerText = data.receipt_number;
    document.getElementById('rcpt-date').innerText = data.payment_date;
    document.getElementById('rcpt-tenant-name').innerText = data.tenant_name;
    document.getElementById('rcpt-tenant-phone').innerText = data.tenant_phone;
    document.getElementById('rcpt-room').innerText = data.room_number ? `Room ${data.room_number}` : 'N/A';
    document.getElementById('rcpt-bed').innerText = data.bed_number ? data.bed_number : 'N/A';
    document.getElementById('rcpt-amount').innerText = `₹${data.amount.toLocaleString('en-IN', {minimumFractionDigits: 2})}`;
    document.getElementById('rcpt-notes').innerText = data.notes || 'Monthly Rent & Maintenance';
    document.getElementById('rcpt-method').innerText = data.payment_method;
    document.getElementById('rcpt-ref').innerText = data.transaction_reference || 'N/A';

    openModal('modal-view-receipt');
  } catch (err) {
    showToast(err.message || 'Error generating receipt', 'error');
  }
}

function shareReceiptOnWhatsApp() {
  if (!currentReceiptData) return;
  const d = currentReceiptData;
  const text = `*LATHA PG FOR GENTS - PAYMENT RECEIPT*\n` +
    `--------------------------------\n` +
    `Receipt No: ${d.receipt_number}\n` +
    `Date: ${d.payment_date}\n` +
    `Tenant: ${d.tenant_name}\n` +
    `Room/Bed: Room ${d.room_number} (${d.bed_number})\n` +
    `Amount Paid: ₹${d.amount.toLocaleString('en-IN')}\n` +
    `Payment Mode: ${d.payment_method} (Ref: ${d.transaction_reference || 'N/A'})\n` +
    `Notes: ${d.notes}\n` +
    `--------------------------------\n` +
    `Thank you for staying at Latha PG!\n` +
    `Helplines: 9353439703 / 9019870803`;

  const phone = d.tenant_phone && d.tenant_phone !== 'N/A' ? d.tenant_phone.replace(/[^0-9]/g, '') : '';
  const url = phone.length >= 10
    ? `https://api.whatsapp.com/send?phone=91${phone.slice(-10)}&text=${encodeURIComponent(text)}`
    : `https://api.whatsapp.com/send?text=${encodeURIComponent(text)}`;

  window.open(url, '_blank');
}

async function handleGenerateInvoice(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const payload = {
    tenant_id: parseInt(formData.get('tenant_id')),
    billing_month: formData.get('billing_month'),
    due_date: formData.get('due_date'),
    rent_amount: parseFloat(formData.get('rent_amount')),
    utility_charges: parseFloat(formData.get('utility_charges') || 0),
  };

  try {
    const res = await fetch(`${API_BASE}/billing/invoices`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to create invoice');
    }
    closeModal('modal-invoice');
    form.reset();
    showToast('Rent invoice generated successfully!');
    refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function handleRaiseComplaint(e) {
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
      throw new Error(err.detail || 'Failed to submit complaint');
    }
    closeModal('modal-complaint');
    form.reset();
    showToast('Maintenance ticket raised successfully!');
    refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function checkoutTenant(tenantId, name) {
  if (!confirm(`Are you sure you want to check out ${name}? This will free their allocated bed.`)) return;
  try {
    const res = await fetch(`${API_BASE}/tenants/${tenantId}/checkout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({}),
    });
    if (!res.ok) throw new Error('Checkout failed');
    showToast(`${name} checked out. Bed is now available!`);
    refreshAllData();
  } catch (err) {
    showToast(err.message, 'error');
  }
}

async function resolveTicket(ticketId) {
  const notes = prompt('Enter resolution notes:', 'Issue repaired and checked');
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

// Service Worker Registration for Offline & Fast Caching
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/dashboard/sw.js')
      .then((reg) => console.log('PWA Service Worker registered:', reg.scope))
      .catch((err) => console.warn('PWA Service Worker registration failed:', err));
  });
}

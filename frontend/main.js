// --- CONFIGURATION ---
const API_BASE_URL = 'http://localhost:8000/api';

// --- AUTHENTICATION ---
function getAuthToken() {
  // Check for both possible token keys to handle any inconsistencies
  let token = localStorage.getItem('auth_token');
  if (!token) {
    token = localStorage.getItem('authToken');
  }
  return token;
}

function isAuthenticated() {
  return !!getAuthToken();
}

// Debug function to check authentication status (for development)
function debugAuth() {
  console.log('=== AUTHENTICATION DEBUG ===');
  console.log('auth_token:', localStorage.getItem('auth_token'));
  console.log('authToken:', localStorage.getItem('authToken'));
  console.log('getAuthToken():', getAuthToken());
  console.log('isAuthenticated():', isAuthenticated());
  console.log('user_data:', localStorage.getItem('user_data'));
  console.log('=============================');
}

function logout() {
  localStorage.removeItem('auth_token');
  localStorage.removeItem('user_data');
  window.location.href = './login.html';
}

function requireAuth() {
  if (!isAuthenticated()) {
    window.location.href = './login.html';
    return false;
  }
  return true;
}

// --- API CALLS ---
async function apiCall(endpoint, options = {}) {
  const token = getAuthToken();
  const defaultHeaders = {
    'Content-Type': 'application/json',
  };
  
  if (token) {
    defaultHeaders['Authorization'] = `Token ${token}`;
  }

  // Debug logging
  console.log('API Call Debug:', {
    endpoint: `${API_BASE_URL}${endpoint}`,
    token: token,
    headers: { ...defaultHeaders, ...options.headers },
    method: options.method || 'GET',
    body: options.body
  });

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: { ...defaultHeaders, ...options.headers },
    ...options
  });

  // Debug response
  console.log('API Response Debug:', {
    status: response.status,
    statusText: response.statusText,
    headers: Object.fromEntries(response.headers.entries())
  });

  // Don't automatically logout on 401 - let the calling function handle it
  // This prevents returning undefined which causes errors
  return response;
}

async function loadAssetPriceHistory(assetId) {
  try {
    const response = await apiCall(`/assets/${assetId}/price-history/`);
    if (response && response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error('Error loading asset price history:', error);
    return null;
  }
}

async function loadDashboardData() {
  try {
    const response = await apiCall('/dashboard/');
    if (response && response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error('Error loading dashboard data:', error);
    return null;
  }
}

async function loadUserAssets() {
  try {
    const response = await apiCall('/assets/');
    if (response && response.ok) {
      return await response.json();
    }
    return [];
  } catch (error) {
    console.error('Error loading assets:', error);
    return [];
  }
}

async function loadUserPortfolios() {
  try {
    const response = await apiCall('/portfolios/');
    if (response && response.ok) {
      return await response.json();
    }
    return [];
  } catch (error) {
    console.error('Error loading portfolios:', error);
    return [];
  }
}

async function evaluateApartment(apartmentData) {
  try {
    const response = await apiCall('/evaluate/apartment/', {
      method: 'POST',
      body: JSON.stringify(apartmentData)
    });
    if (response && response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error('Error evaluating apartment:', error);
    return null;
  }
}

async function createAsset(assetData) {
  try {
    const response = await apiCall('/assets/', {
      method: 'POST',
      body: JSON.stringify(assetData)
    });
    if (response && response.ok) {
      return await response.json();
    } else {
      // Log the error response to see what's wrong
      const errorText = await response.text();
      console.error('Asset creation failed:', response.status, errorText);
      return null;
    }
  } catch (error) {
    console.error('Error creating asset:', error);
    return null;
  }
}

// --- DATA ---
let assets = [];
let portfolios = [];
let dashboardData = {};

// District and Mahalla data (using Latin names from CSV for the model)
const districtMahallas = {
  "Bektemir tumani": ["Abay mahallasi", "Mirishkor mahallasi", "Oltintopgan mahallasi", "Husayn Boyqaro mahallasi", "Rohat mahallasi", "Zabardast mahallasi", "Musaffo mahallasi", "Sohil mahallasi", "Zilola mahallasi", "Nurafshon mahallasi", "Nurliyo'l mahallasi", "Gulbog' mahallasi", "Iykota mahallasi", "Majnuntol mahallasi", "Chashma mahallasi", "Bektemir mahallasi", "Ustozlar mahallasi", "Iqbol mahallasi"],
  "Chilonzor tumani": ["Al-Xorazmiy mahallasi", "Gavhar mahallasi", "Bo'rijar mahallasi", "Guliston mahallasi", "Tirsakobod mahallasi", "Bekto'pi mahallasi", "Beshqo'rg'on mahallasi", "Lutfiy mahallasi", "Sharq mahallasi", "Yakkabog' mahallasi", "Charx Kamolon-3 mahallasi", "Dilobod mahallasi", "Katta Qozirabot mahallasi", "Beshchinor mahallasi", "Xayrobod mahallasi", "Xonto'pi mahallasi", "Katta Chilonzor-2 mahallasi", "Bog'zor mahallasi", "Bahoriston mahallasi", "Yakkatut mahallasi", "Do'mbirobod mahallasi", "Katta Do'mbirobod mahallasi", "Zarqo'rg'on mahallasi", "Qatortol-2 mahallasi", "Ko'tarma mahallasi", "Katta Xirmontepa mahallasi", "Katta Chilonzor-1 mahallasi", "Katta Navbahor mahallasi", "Mehrjon mahallasi", "Chilonzor-Oqtepa mahallasi", "Navbahor mahallasi", "Mevazor mahallasi", "Katta Olmazor mahallasi", "Fidokor mahallasi", "Xalqlar do'stligi mahallasi", "Sharq tongi mahallasi", "Charx Kamolon-2 mahallasi", "Sharaf mahallasi", "Xirmontepa mahallasi", "Botirma mahallasi", "Kichik Xirmontepa mahallasi", "Nafosat mahallasi", "Naqqoshlik mahallasi", "Qatortol mahallasi", "Shuhrat mahallasi", "Cho'ponota mahallasi", "Qatortol-1 mahallasi", "Beshyog'och mahallasi", "Chilonzor mahallasi", "Novza mahallasi", "Charx Kamolon-1 mahallasi", "Ko'rkam mahallasi", "Diyor mahallasi", "Qozirabot mahallasi", "Katta Chilonzor-3 mahallasi"],
  "Mirobod tumani": ["Bayot mahallasi", "Tong yulduzi mahallasi", "Yangi Qo'yliq mahallasi", "Mirobod mahallasi", "Qo'yliqota mahallasi", "Sariko'l mahallasi", "Qorasuv mahallasi", "Navro'z mahallasi", "Baynalmilal mahallasi", "Parvona mahallasi", "Temiryo'lchilar mahallasi", "Movarounnahr mahallasi", "Abdulla Avloniy mahallasi", "Oquy mahallasi", "Afrosiyob mahallasi", "At-Termiziy mahallasi", "Yangi Mirobod mahallasi", "Tolariq mahallasi", "Farovon mahallasi", "Oybek mahallasi", "Sharof Rashidov mahallasi", "Ziyonur mahallasi", "Lolazor mahallasi", "Zaminobod mahallasi", "Barotxo'ja mahallasi", "Banokatiy mahallasi", "Chinor mahallasi", "Birodarlik mahallasi", "Bilimdon mahallasi", "Abdurauf Fitrat mahallasi", "Yangizamon mahallasi", "Mingo'rik mahallasi", "Oltinko'l mahallasi", "Inoqobod mahallasi", "Salor mahallasi", "Fayziobod mahallasi", "Furqat mahallasi", "Istiqlolobod mahallasi", "Yuksalish mahallasi"],
  "Mirzo Ulug'bek tumani": ["Olimlar mahallasi", "Ahillik mahallasi", "Asaka mahallasi", "Mirzakalon Ismoiliy mahallasi", "Oqqo'rg'on mahallasi", "Buyuk ipak yo'li mahallasi", "Ulug'bek mahallasi", "Oydin mahallasi", "Yangi Avayxon mahallasi", "Bog'imaydon mahallasi", "Oqibat mahallasi", "Darxon mahallasi", "Bo'z mahallasi", "Shahrisabz mahallasi", "Habib Abdullayev mahallasi", "Katta Qorasuv mahallasi", "Shalola mahallasi", "Lashkarbegi mahallasi", "Gulsanam mahallasi", "Sultoniya mahallasi", "Chimyon mahallasi", "Shukur Burhonov mahallasi", "Ijodkor mahallasi", "Oliyhimmat mahallasi", "Sho'rtepa mahallasi", "Mustaqillik mahallasi", "Jasorat mahallasi", "Traktorsozlar mahallasi", "Olmachi mahallasi", "Al-Forobiy mahallasi", "Yalang'och mahallasi", "Navnihol mahallasi", "Shahriobod mahallasi", "Sarbon mahallasi", "Bahor mahallasi", "Hamid Olimjon mahallasi", "Katta Yalang'ochota mahallasi", "Azamat mahallasi", "Geofizika mahallasi", "Oltintepa mahallasi", "Feruza mahallasi", "Turon mahallasi", "Geologlar mahallasi", "Yangi Kamolot mahallasi", "Ahmad Yugnakiy mahallasi", "Uyg'onish mahallasi", "Gulzorobod mahallasi", "Munavvarqori mahallasi", "Yuzrabot mahallasi", "Nur mahallasi", "Minglola mahallasi", "Temuriylar mahallasi", "Alisherobod mahallasi", "Sayram mahallasi", "Elobod mahallasi", "Yangi Olmachi mahallasi", "Avayxon mahallasi", "Nodirabegim mahallasi", "Alpomish mahallasi", "Ko'hna Mevazor mahallasi", "Podshobog' mahallasi", "Humoyun mahallasi", "Iqtidor mahallasi", "Katta Oltintepa mahallasi", "Kamolot mahallasi", "Beshkapa mahallasi", "Zakovat mahallasi", "Alisher Navoiy mahallasi", "Chingeldi mahallasi", "Pastkiyuz mahallasi"],
  "Olmazor tumani": ["Shon-shuhrat mahallasi", "Tabassum mahallasi", "Namuna mahallasi", "Tepaguzar mahallasi", "Achaobod mahallasi", "Eskishahar mahallasi", "Chustiy mahallasi", "Allon mahallasi", "Elparvar mahallasi", "Qichqiriq mahallasi", "Gulzor mahallasi", "Shifokorlar mahallasi", "Chig'atoy-Oqtepa mahallasi", "Beruniy mahallasi", "Miskin mahallasi", "Olimpiya mahallasi", "Yuqori Beshqo'rg'on mahallasi"],
  "Shayxontohur tumani": ["Oqlon mahallasi", "Chaqar mahallasi", "Labzak mahallasi", "Yangishahar mahallasi", "Ibn Sino mahallasi", "Tinchlik mahallasi", "Shofayzi mahallasi", "Eshonguzar mahallasi", "Bog'ko'cha mahallasi", "Ilg'or mahallasi", "Kattahovuz mahallasi", "Yangi Beltepa mahallasi", "Sarxumdon mahallasi", "Yangi Jarariq mahallasi", "Jarariq mahallasi", "Ko'kcha Darvoza mahallasi", "Beltepa mahallasi", "Katta Jarariq mahallasi", "Xadra mahallasi", "Olmazor mahallasi", "Kohota mahallasi", "Shayxontohur mahallasi", "O'qchi mahallasi", "Gulobod mahallasi", "Gulbozor mahallasi", "Janggoh mahallasi", "Chorsu mahallasi", "Bo'ston mahallasi", "Ipakchi mahallasi", "Yangi Kamolon mahallasi", "Suzukota mahallasi", "Taxtapul mahallasi", "Olim Xo'jayev mahallasi", "Charxnovza mahallasi", "Katta Oqtepa mahallasi", "Samarqand Darvoza mahallasi", "Huvaydo mahallasi", "Shodlik mahallasi", "Zafarobod mahallasi", "Kamolon mahallasi", "Kattabog' mahallasi", "Obinazir mahallasi", "Eski Jarariq mahallasi", "O'zbekiston mahallasi", "Kamolon Darvoza mahallasi", "Ko'kcha mahallasi", "Qoratosh mahallasi", "Yangiobod mahallasi", "Mannon Uyg'ur mahallasi", "O'rda mahallasi", "Zangiota mahallasi"],
  "Yakkasaray tumani": ["Zarkent mahallasi", "Hamza mahallasi", "Eski Shahar mahallasi", "Asaka mahallasi", "Yangishahar mahallasi", "Bog'ishton mahallasi", "Ayniy mahallasi", "Tahrir mahallasi", "Xonobod mahallasi", "Qalqoq mahallasi", "Shifokorlar mahallasi", "Fidoiy mahallasi", "Shahrisabz mahallasi", "Zulfiyaxonim mahallasi", "Navbahor mahallasi", "Eshonqul mahallasi", "Ko'hna Cho'ponota mahallasi", "Kanoat mahallasi", "Taraqqiyot mahallasi", "Lux mahallasi", "Katartol mahallasi", "Yakkasaray mahallasi", "Fayzulla Xo'jayev mahallasi"],
  "Yunusobod tumani": ["Fayzulla Xo'jayev mahallasi", "Yunusobod mahallasi", "Shohid Rahimov mahallasi", "Sharq mahallasi", "Qadimjoy mahallasi", "Malika mahallasi", "Ahmad Donish mahallasi", "Bodomzor mahallasi", "Zarkent mahallasi", "Tinchlik mahallasi", "Bobur mahallasi"],
  "Yashnobod tumani": ["Navruz mahallasi", "Tinchlik mahallasi", "Buston mahallasi", "Quvvat mahallasi", "Yoshnobod mahallasi", "Nurzod mahallasi", "Turon mahallasi", "Yuldosh mahallasi", "Fayz mahallasi", "Erkin mahallasi", "Toshkent mahallasi", "Dizel mahallasi", "Yaxshibogcha mahallasi", "Gulshan mahallasi", "Beruniy mahallasi", "Yoshlik mahallasi", "Nafosat mahallasi", "Mingurik mahallasi", "Qadimiy mahallasi", "Xadra mahallasi", "Dustlik mahallasi", "Mergenli mahallasi", "Xayratobod mahallasi", "Kelishganda mahallasi", "Imom Buxoriy mahallasi", "Abdurazzok mahallasi", "Paxtakor mahallasi", "Nur mahallasi", "Hamza mahallasi", "Pushkin mahallasi", "Namuna mahallasi", "Ismoil Somoniy mahallasi", "Mustaqillik mahallasi", "Zilola mahallasi"],
  "Sergeli tumani": ["Shayxontohur mahallasi", "Yangihayot mahallasi", "Sergeli mahallasi", "Umarobod mahallasi", "Mehnatobod mahallasi", "Kubo mahallasi", "Chilonzor mahallasi", "Abubakr mahallasi", "Kiron mahallasi", "Bozsuv mahallasi", "Orolboy mahallasi", "Xonobod mahallasi", "Gulbahor mahallasi", "Darxon mahallasi", "Savdogar mahallasi", "Gazalkent mahallasi", "Turon mahallasi", "Yangi Hayot-3 mahallasi", "Ravshan mahallasi", "Navbahor mahallasi", "Yangi Hayot-2 mahallasi", "Xosilot mahallasi", "Oksoy mahallasi", "Xushor mahallasi", "Fitrat mahallasi", "Qungirot mahallasi", "Navro'z mahallasi", "Oltin Vodiyi mahallasi", "Kelishganda mahallasi", "Xursand mahallasi", "Yangi Hayot-1 mahallasi", "Istiqlol mahallasi", "Dostlik mahallasi", "Buyuk Ipak Yo'li mahallasi", "Umid mahallasi", "Qoshchinor mahallasi", "Yangi Sergeli mahallasi", "Oila mahallasi", "Merganli mahallasi", "Sharq mahallasi", "Kelishganda-2 mahallasi", "Gulo mahallasi"],
  "Uchtepa tumani": ["Mustaqillik mahallasi", "Uchtepa mahallasi", "Tinchlik mahallasi", "Hashtepa mahallasi", "Beshqurgan mahallasi", "Dustlik mahallasi", "Bibikuxna mahallasi", "Qarasuv mahallasi", "Bo'z mahallasi", "Aktepa mahallasi", "Katta Uchtepa mahallasi", "Quylyuk mahallasi", "Navbahor mahallasi", "Turakurgan mahallasi", "Ko'hna Uchtepa mahallasi", "Shurkurgan mahallasi", "Oltintog' mahallasi", "Oltin mahallasi", "Yangi Hayot mahallasi", "Istiqlol mahallasi", "Shifokorlar mahallasi", "Sadriya mahallasi", "Omonxona mahallasi", "Yangi mahallasi", "Navro'z mahallasi", "Zafar mahallasi", "Bog'iriboshi mahallasi", "Bovuchcha mahallasi"]
};

// --- STATE MANAGEMENT ---
let currentView = 'dashboard' // 'dashboard', 'asset-detail', 'add-asset', 'evaluate'
let selectedAssetId = null
let currentEvaluationResult = null

// --- DOM ELEMENTS ---
const viewContainer = document.getElementById('views-container')
const dashboardView = document.getElementById('dashboard-view')
const assetDetailView = document.getElementById('asset-detail-view')
const addAssetView = document.getElementById('add-asset-view')
const evaluateView = document.getElementById('evaluate-view')
const pageTitle = document.getElementById('page-title')
const backButton = document.getElementById('back-button')

// --- INITIALIZATION ---
async function initApp() {
  console.log('Initializing app...');
  console.log('Auth token:', getAuthToken());
  
  if (!requireAuth()) return;
  
  // Load user profile from API
  const userData = await loadUserProfile();
  console.log('Loaded user data from API:', userData);
  
  // Update user profile in UI
  if (userData) {
    updateUserProfile(userData);
    
    // Update user avatar with initials
    const avatarElement = document.querySelector('#profile img');
    if (avatarElement) {
      let initials = 'П'; // Default initial in Russian
      
      if (userData.first_name || userData.last_name) {
        const firstName = userData.first_name || '';
        const lastName = userData.last_name || '';
        initials = (firstName.charAt(0) + lastName.charAt(0)).toUpperCase() || 'П';
      } else if (userData.email) {
        const emailPrefix = userData.email.split('@')[0];
        const nameParts = emailPrefix.split(/[._-]/);
        if (nameParts.length >= 2) {
          initials = (nameParts[0].charAt(0) + nameParts[1].charAt(0)).toUpperCase();
        } else if (nameParts.length === 1) {
          initials = nameParts[0].charAt(0).toUpperCase();
        }
      }
      
      // Use a blue background with white text for the avatar
      avatarElement.src = `https://placehold.co/100x100/4F46E5/FFFFFF?text=${encodeURIComponent(initials)}`;
      avatarElement.alt = `User Avatar`;
    }
    
    // Store user data in localStorage for future reference
    localStorage.setItem('user_data', JSON.stringify(userData));
  } else {
    // Fallback to localStorage if API call fails
    const storedUserData = JSON.parse(localStorage.getItem('user_data') || '{}');
    updateUserProfile(storedUserData);
  }
  
  // Load dashboard data
  await loadAppData();
  
  // Initialize UI
  initializeEventListeners();
  navigateTo('dashboard');
  
  // Initialize Lucide icons
  lucide.createIcons();
}

async function loadAppData() {
  try {
    // Load data in parallel
    const [dashboardResponse, assetsResponse, portfoliosResponse] = await Promise.all([
      loadDashboardData(),
      loadUserAssets(),
      loadUserPortfolios()
    ]);
    
    dashboardData = dashboardResponse || {};
    assets = assetsResponse || [];
    portfolios = portfoliosResponse || [];
    
    // Create default portfolio if none exists
    if (portfolios.length === 0) {
      const defaultPortfolio = await createDefaultPortfolio();
      if (defaultPortfolio) {
        console.log('Created default portfolio:', defaultPortfolio);
      }
    }
    
    console.log('Loaded data:', { dashboardData, assets, portfolios });
  } catch (error) {
    console.error('Error loading app data:', error);
  }
}

function updateUserProfile(userData) {
  console.log('Updating user profile with:', userData);
  
  // Update user name
  const nameElement = document.getElementById('user-name');
  let displayName = 'Пользователь';
  let initials = 'У'; // Default initial in Russian
  
  if (nameElement) {
    // Priority 1: Use the actual name entered during registration (username field)
    if (userData.username && userData.username !== userData.email) {
      displayName = userData.username;
      // Get initials from username
      const nameParts = userData.username.split(/\s+/);
      if (nameParts.length >= 2) {
        initials = (nameParts[0].charAt(0) + nameParts[nameParts.length - 1].charAt(0)).toUpperCase();
      } else {
        initials = userData.username.charAt(0).toUpperCase();
      }
    }
    // Priority 2: Use first_name and last_name if available
    else if (userData.first_name || userData.last_name) {
      displayName = `${userData.first_name || ''} ${userData.last_name || ''}`.trim();
      // Get initials from first and last name
      const firstName = userData.first_name || '';
      const lastName = userData.last_name || '';
      initials = (firstName.charAt(0) + lastName.charAt(0)).toUpperCase() || 'У';
    } 
    // Priority 3: Extract name from email as fallback
    else if (userData.email) {
      // Extract name from email (e.g., "temurbek.khasanboev@gmail.com" -> "Temurbek Khasanboev")
      const emailPrefix = userData.email.split('@')[0];
      const nameParts = emailPrefix.split(/[._-]/);
      displayName = nameParts
        .map(part => part.charAt(0).toUpperCase() + part.slice(1).toLowerCase())
        .join(' ') || 'Пользователь';
      
      // Get initials from email parts
      if (nameParts.length >= 2) {
        initials = (nameParts[0].charAt(0) + nameParts[1].charAt(0)).toUpperCase();
      } else if (nameParts.length === 1) {
        initials = nameParts[0].charAt(0).toUpperCase();
      }
    }
    
    nameElement.textContent = displayName;
  }
  
  // Update user avatar with initials
  const avatarElement = document.querySelector('#profile img');
  if (avatarElement) {
    avatarElement.src = `https://placehold.co/100x100/4F46E5/FFFFFF?text=${encodeURIComponent(initials)}`;
    avatarElement.alt = `${displayName} Avatar`;
  }
  
  // Update user avatar with initials
  updateUserAvatar(userData);
  
  // Update user plan
  const planElement = document.getElementById('user-plan');
  if (planElement) {
    // You can customize this based on your user data structure
    planElement.textContent = userData.plan || 'Базовый план';
  }
}

function initializeEventListeners() {
  // Logout button
  document.getElementById('logout-btn').addEventListener('click', (e) => {
    e.preventDefault();
    logout();
  });
  
  // Add asset button
  document.getElementById('add-asset-btn-header').addEventListener('click', () => {
    navigateTo('add-asset');
  });
  
  // Back button
  backButton.addEventListener('click', () => {
    navigateTo('dashboard');
  });
  
  // Navigation
  document.getElementById('nav-dashboard').addEventListener('click', (e) => {
    e.preventDefault();
    navigateTo('dashboard');
  });
  
  // Evaluate navigation
  document.getElementById('nav-evaluate').addEventListener('click', (e) => {
    e.preventDefault();
    navigateTo('evaluate');
  });

  // Market navigation
  document.getElementById('nav-market').addEventListener('click', (e) => {
    e.preventDefault();
    navigateTo('market');
  });

  // Announcements navigation
  document.getElementById('nav-announcements').addEventListener('click', (e) => {
    e.preventDefault();
    navigateTo('announcements');
  });

  // AI Assistant navigation
  document.getElementById('nav-ai-assistant').addEventListener('click', (e) => {
    e.preventDefault();
    navigateTo('ai-assistant');
  });
}

// --- RENDER FUNCTIONS ---

// Renders the main dashboard
async function renderDashboard() {
  // Update summary cards with real data
  const totalValue = dashboardData.total_value || 0;
  const totalChange = dashboardData.total_change || 0;
  const changePercent = dashboardData.change_percent || 0;
  const assetCount = dashboardData.asset_count || 0;

  document.getElementById('total-value').textContent = `$${totalValue.toLocaleString('en-US', {maximumFractionDigits: 0})}`
  const changeElement = document.getElementById('total-change')
  changeElement.textContent = `${totalChange > 0 ? '+' : ''}${changePercent.toFixed(1)}%`
  changeElement.className = `text-2xl font-bold ${totalChange > 0 ? 'text-green-500' : 'text-red-500'}`

  document.getElementById('asset-count').textContent = assetCount

  // Render asset cards
  const assetsGrid = document.getElementById('assets-grid')
  assetsGrid.innerHTML = '' // Clear existing cards
  
  if (assets.length === 0) {
    assetsGrid.innerHTML = `
      <div class="col-span-full text-center py-12">
        <div class="text-gray-400 dark:text-gray-600 mb-4">
          <i data-lucide="folder-open" class="w-16 h-16 mx-auto mb-4"></i>
          <h3 class="text-lg font-semibold mb-2">Пока нет активов</h3>
          <p class="text-sm">Добавьте свой первый актив, чтобы начать отслеживание портфеля</p>
        </div>
        <button onclick="navigateTo('add-asset')" class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition">
          <i data-lucide="plus" class="mr-2 h-5 w-5 inline"></i>
          Добавить первый актив
        </button>
      </div>
    `;
    lucide.createIcons();
    return;
  }
  
  // Use all_assets from dashboard data which includes change_percentage for all assets
  const assetsWithChanges = dashboardData.all_assets || dashboardData.recent_assets || assets;
  
  assetsWithChanges.forEach((asset) => {
    // Use real change percentage from API, fallback to 0 if not available
    const changePercent = asset.change_percentage || 0;
    const currentValue = parseFloat(asset.current_value);
    
    // Calculate absolute change amount from percentage
    let change = 0;
    if (changePercent !== 0) {
      const pastValue = currentValue / (1 + changePercent / 100);
      change = currentValue - pastValue;
    }

    const assetTypeDisplay = {
      'apartment': 'Квартира',
      'car': 'Авто'
    };

    const assetTypeClass = {
      'apartment': 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300',
      'car': 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300'
    };

    const card = `
      <div class="asset-card bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden cursor-pointer" onclick="navigateTo('asset-detail', ${asset.id})">
        <div class="w-full h-40 bg-gradient-to-br ${asset.asset_type === 'apartment' ? 'from-blue-400 to-blue-600' : 'from-green-400 to-green-600'} flex items-center justify-center">
          <i data-lucide="${asset.asset_type === 'apartment' ? 'building-2' : 'car'}" class="w-16 h-16 text-white"></i>
        </div>
                        <div class="p-4">
                            <div class="flex justify-between items-start">
                                <div>
              <p class="text-sm text-gray-500 dark:text-gray-400">${asset.address || 'Не указано'}</p>
                                    <h3 class="font-bold text-lg">${asset.name}</h3>
                                </div>
            <span class="text-xs font-semibold px-2 py-1 rounded-full ${assetTypeClass[asset.asset_type] || assetTypeClass['apartment']}">
              ${assetTypeDisplay[asset.asset_type] || 'Актив'}
                                </span>
                            </div>
                            <div class="mt-4 flex justify-between items-center">
            <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">$${parseFloat(asset.current_value).toLocaleString('en-US', {maximumFractionDigits: 0})}</p>
                                <div class="text-right">
              <p class="font-semibold ${changePercent > 0 ? 'text-green-500' : changePercent < 0 ? 'text-red-500' : 'text-gray-500'}">
                                        ${changePercent > 0 ? '+' : ''}${changePercent.toFixed(1)}%
                                    </p>
                                    <p class="text-sm text-gray-500 dark:text-gray-400">(30 д.)</p>
                                </div>
                            </div>
                        </div>
                    </div>
    `;
    assetsGrid.innerHTML += card;
  });
  
  // Reinitialize Lucide icons
  lucide.createIcons();
}

// Renders the detailed asset view
async function renderAssetDetail(assetId) {
  const asset = assets.find((a) => a.id === assetId)
  if (!asset) return

  // Parse asset details if it's a JSON string
  let assetDetails = {};
  try {
    assetDetails = asset.description ? JSON.parse(asset.description) : {};
  } catch (e) {
    console.error('Error parsing asset details:', e);
  }

  assetDetailView.innerHTML = `
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div class="lg:col-span-2 space-y-6">
                        <!-- Header -->
                        <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
                            <div class="flex flex-col md:flex-row gap-6">
            <div class="w-full md:w-1/3 h-48 bg-gradient-to-br ${asset.asset_type === 'apartment' ? 'from-blue-400 to-blue-600' : 'from-green-400 to-green-600'} rounded-lg flex items-center justify-center">
              <i data-lucide="${asset.asset_type === 'apartment' ? 'building-2' : 'car'}" class="w-20 h-20 text-white"></i>
            </div>
                                <div class="flex-1">
              <p class="text-sm text-gray-500 dark:text-gray-400">${asset.address || 'Не указано'}</p>
                                    <h3 class="text-3xl font-bold mb-4">${asset.name}</h3>
                                    <div class="flex items-center space-x-6 mb-4">
                                        <div>
                                            <p class="text-sm text-gray-500 dark:text-gray-400">Рыночная стоимость</p>
                  <p class="text-2xl font-bold text-blue-600 dark:text-blue-400">$${parseFloat(asset.current_value).toLocaleString('en-US', {maximumFractionDigits: 0})}</p>
                                        </div>
                                        </div>
              <div class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                <p><strong>Дата добавления:</strong> ${new Date(asset.created_at).toLocaleDateString('ru-RU')}</p>
                <p><strong>Последнее обновление:</strong> ${new Date(asset.updated_at).toLocaleDateString('ru-RU')}</p>
                                    </div>
                                    <button class="w-full bg-blue-600 text-white px-4 py-3 rounded-lg flex items-center justify-center hover:bg-blue-700 transition">
                <i data-lucide="edit" class="mr-2 h-5 w-5"></i>
                Редактировать актив
                                    </button>
                                </div>
                            </div>
                        </div>

                        <!-- Analytics -->
                        <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
                            <h4 class="text-xl font-bold mb-4">История стоимости</h4>
          <div class="h-80">
            <canvas id="price-history-chart"></canvas>
          </div>
                        </div>
                        
        ${asset.asset_type === 'apartment' ? `
                        <!-- Map -->
                        <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
                            <h4 class="text-xl font-bold mb-4">Расположение и инфраструктура</h4>
          <div class="h-64 bg-gray-50 dark:bg-gray-700 rounded-lg flex items-center justify-center">
            <div class="text-center text-gray-500 dark:text-gray-400">
              <i data-lucide="map-pin" class="w-12 h-12 mx-auto mb-2"></i>
              <p>Карта будет доступна<br>в следующих обновлениях</p>
                        </div>
          </div>
                        </div>
        ` : ''}
                    </div>

                    <div class="space-y-6">
                        <!-- Parameters -->
                        <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
                             <h4 class="text-xl font-bold mb-4">Параметры</h4>
                             <ul class="space-y-2 text-sm">
            <li class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Тип</span>
              <span class="font-semibold">${asset.asset_type === 'apartment' ? 'Квартира' : 'Автомобиль'}</span>
            </li>
            ${asset.address ? `
            <li class="flex justify-between">
              <span class="text-gray-500 dark:text-gray-400">Местоположение</span>
              <span class="font-semibold">${asset.address}</span>
            </li>
            ` : ''}
            ${Object.entries(assetDetails).map(([key, value]) => `
                                    <li class="flex justify-between">
                                        <span class="text-gray-500 dark:text-gray-400">${key}</span>
                                        <span class="font-semibold">${value}</span>
                                    </li>
            `).join('')}
                             </ul>
                        </div>

        <!-- Portfolio Info -->
                        <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h4 class="text-xl font-bold mb-4">Портфель</h4>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Этот актив входит в портфель:
          </p>
          <p class="font-semibold mt-1">${asset.portfolio ? asset.portfolio.name || 'Основной портфель' : 'Не указан'}</p>
                        </div>

        <!-- Actions -->
                        <div class="bg-white dark:bg-gray-800 rounded-xl shadow p-6">
          <h4 class="text-xl font-bold mb-4">Действия</h4>
          <div class="space-y-2">
            <button id="update-evaluation-btn" data-asset-id="${asset.id}" class="w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition text-sm">
              <i data-lucide="refresh-cw" class="mr-2 h-4 w-4 inline"></i>
              Обновить оценку
            </button>
            <button id="delete-asset-btn" data-asset-id="${asset.id}" class="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition text-sm">
              <i data-lucide="trash-2" class="mr-2 h-4 w-4 inline"></i>
              Удалить актив
            </button>
            <button id="put-in-sales-btn" data-asset-id="${asset.id}" class="w-full bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700 transition text-sm">
              <i data-lucide="tag" class="mr-2 h-4 w-4 inline"></i>
              Выставить на продажу
            </button>
                        </div>
                    </div>
                </div>
                </div>
  `;

  // Reinitialize Lucide icons
  lucide.createIcons();

  // Add event listeners for action buttons
  const updateBtn = document.getElementById('update-evaluation-btn');
  const deleteBtn = document.getElementById('delete-asset-btn');
  const salesBtn = document.getElementById('put-in-sales-btn');

  if (updateBtn) {
    updateBtn.addEventListener('click', () => handleUpdateEvaluation(asset));
  }

  if (deleteBtn) {
    deleteBtn.addEventListener('click', () => handleDeleteAsset(asset));
  }

  if (salesBtn) {
    salesBtn.addEventListener('click', () => handlePutInSales(asset));
  }

  // Load and render price history chart
  await renderPriceHistoryChart(assetId);
}

async function renderPriceHistoryChart(assetId) {
  try {
    const priceHistory = await loadAssetPriceHistory(assetId);
    
    if (!priceHistory || !priceHistory.price_history || priceHistory.price_history.length === 0) {
      // Show placeholder if no data
      const chartContainer = document.getElementById('price-history-chart').parentElement;
      chartContainer.innerHTML = `
        <div class="h-80 flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded-lg">
          <div class="text-center text-gray-500 dark:text-gray-400">
            <i data-lucide="trending-up" class="w-12 h-12 mx-auto mb-2"></i>
            <p>История стоимости будет доступна<br>после добавления данных</p>
          </div>
        </div>
      `;
      lucide.createIcons();
      return;
    }

    const ctx = document.getElementById('price-history-chart').getContext('2d');
    
    // Prepare data for Chart.js - include historical data + current value
    let labels = priceHistory.price_history.map(entry => entry.month);
    let data = priceHistory.price_history.map(entry => entry.value);
    
    // Add current month/value as the last point if not already included
    const currentDate = new Date();
    const currentMonthLabel = currentDate.toLocaleDateString('ru-RU', { month: 'short', year: 'numeric' });
    
    if (!labels.includes(currentMonthLabel)) {
      labels.push(currentMonthLabel);
      data.push(priceHistory.current_value);
    } else {
      // Update the last entry to current value if it's the same month
      const lastIndex = labels.length - 1;
      if (labels[lastIndex] === currentMonthLabel) {
        data[lastIndex] = priceHistory.current_value;
      }
    }
    
    // Calculate gradient colors
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(59, 130, 246, 0.4)');
    gradient.addColorStop(0.6, 'rgba(59, 130, 246, 0.1)');
    gradient.addColorStop(1, 'rgba(59, 130, 246, 0.02)');
    
    // Create special styling for the current point
    const pointColors = data.map((_, index) => 
      index === data.length - 1 ? 'rgb(16, 185, 129)' : 'rgb(59, 130, 246)'
    );
    const pointBorderColors = data.map((_, index) => 
      index === data.length - 1 ? 'white' : 'white'
    );
    const pointRadii = data.map((_, index) => 
      index === data.length - 1 ? 8 : 6
    );
    
    // Destroy existing chart if it exists
    if (window.priceHistoryChart) {
      window.priceHistoryChart.destroy();
    }
    
    // Create new chart
    window.priceHistoryChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Стоимость ($)',
          data: data,
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: gradient,
          borderWidth: 3,
          fill: true,
          tension: 0.4,
          pointBackgroundColor: pointColors,
          pointBorderColor: pointBorderColors,
          pointBorderWidth: 3,
          pointRadius: pointRadii,
          pointHoverRadius: 10,
          pointHoverBackgroundColor: pointColors,
          pointHoverBorderColor: 'white',
          pointHoverBorderWidth: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        layout: {
          padding: {
            top: 20,
            bottom: 30,
            left: 10,
            right: 10
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            backgroundColor: 'rgba(0, 0, 0, 0.85)',
            titleColor: 'white',
            bodyColor: 'white',
            borderColor: 'rgb(59, 130, 246)',
            borderWidth: 2,
            cornerRadius: 12,
            displayColors: false,
            titleFont: {
              size: 14,
              weight: 'bold'
            },
            bodyFont: {
              size: 13
            },
            padding: 12,
            callbacks: {
              title: function(context) {
                const isCurrentMonth = context[0].dataIndex === data.length - 1;
                return context[0].label + (isCurrentMonth ? ' (текущая)' : '');
              },
              label: function(context) {
                return `$${context.parsed.y.toLocaleString('en-US', {maximumFractionDigits: 0})}`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: {
              display: false
            },
            ticks: {
              color: 'rgb(107, 114, 128)',
              font: {
                size: 11
              },
              maxRotation: 45,
              minRotation: 0,
              padding: 8,
              callback: function(value, index) {
                // Show every other label to avoid crowding
                if (labels.length > 8 && index % 2 !== 0) {
                  return '';
                }
                return this.getLabelForValue(value);
              }
            },
            border: {
              display: false
            }
          },
          y: {
            grid: {
              color: 'rgba(107, 114, 128, 0.08)',
              borderDash: [5, 5]
            },
            ticks: {
              color: 'rgb(107, 114, 128)',
              font: {
                size: 11
              },
              padding: 12,
              callback: function(value) {
                return '$' + value.toLocaleString('en-US', {maximumFractionDigits: 0});
              }
            },
            border: {
              display: false
            }
          }
        },
        interaction: {
          intersect: false,
          mode: 'index'
        },
        animation: {
          duration: 2500,
          easing: 'easeInOutCubic'
        }
      }
    });
    
    // Add change percentage info
    const changePercentage = priceHistory.change_percentage || 0;
    const changeColor = changePercentage >= 0 ? 'text-green-600' : 'text-red-600';
    const changeIcon = changePercentage >= 0 ? 'trending-up' : 'trending-down';
    
    // Add change indicator above the chart
    const chartContainer = document.getElementById('price-history-chart').parentElement;
    const changeIndicator = document.createElement('div');
    changeIndicator.className = 'flex items-center justify-between mb-4';
    changeIndicator.innerHTML = `
      <div class="flex items-center space-x-2">
        <i data-lucide="${changeIcon}" class="w-5 h-5 ${changeColor}"></i>
        <span class="${changeColor} font-semibold">
          ${changePercentage > 0 ? '+' : ''}${changePercentage.toFixed(2)}% за 30 дней
        </span>
      </div>
      <div class="text-sm text-gray-500 dark:text-gray-400">
        Текущая стоимость: $${priceHistory.current_value.toLocaleString('en-US', {maximumFractionDigits: 0})}
      </div>
    `;
    
    chartContainer.insertBefore(changeIndicator, chartContainer.firstChild);
    lucide.createIcons();
    
  } catch (error) {
    console.error('Error rendering price history chart:', error);
    
    // Show error message
    const chartContainer = document.getElementById('price-history-chart').parentElement;
    chartContainer.innerHTML = `
      <div class="h-80 flex items-center justify-center bg-gray-50 dark:bg-gray-700 rounded-lg">
        <div class="text-center text-gray-500 dark:text-gray-400">
          <i data-lucide="alert-circle" class="w-12 h-12 mx-auto mb-2"></i>
          <p>Ошибка загрузки данных<br>истории стоимости</p>
        </div>
      </div>
    `;
    lucide.createIcons();
  }
}

// Renders the form for a specific asset type
function renderAddAssetForm(assetType) {
  const step2 = document.getElementById('wizard-step-2')
  let formHtml = ''

  if (assetType === 'apartment') {
    formHtml = `
                    <h3 class="text-2xl font-bold mb-6">Параметры квартиры</h3>
                    <form id="add-asset-form" class="space-y-4">
        <input type="hidden" name="asset_type" value="apartment">
        
        <!-- Asset Basic Info -->
                        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Название актива</label>
          <input type="text" name="name" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" placeholder="Например: 2-комн. квартира на Навои">
                        </div>
        
                         <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Адрес</label>
          <input type="text" name="location" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" placeholder="ул. Навои, 15, Ташкент">
                        </div>

        <!-- Portfolio Selection -->
                        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Портфель</label>
          <select name="portfolio_id" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
            <option value="">Выберите портфель...</option>
            ${portfolios.map(portfolio => `<option value="${portfolio.id}">${portfolio.name}</option>`).join('')}
          </select>
          <button type="button" id="create-portfolio-btn" class="mt-2 text-sm text-blue-600 hover:text-blue-700">+ Создать новый портфель</button>
                        </div>

        <!-- Basic Apartment Fields -->
        <div class="grid grid-cols-2 gap-4">
                        <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Кол-во комнат</label>
            <input type="number" name="rooms" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" min="1" value="3">
                        </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Площадь (м²)</label>
            <input type="number" name="area" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" min="1" value="75">
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Этаж</label>
            <input type="number" name="floor" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" min="1" value="4">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Всего этажей</label>
            <input type="number" name="total_floors" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" min="1" value="9">
          </div>
        </div>

        <!-- Location -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Район *</label>
            <select name="district" id="district-select" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
              <option value="">Выберите район...</option>
              ${Object.keys(districtMahallas).map(district => `<option value="${district}">${district}</option>`).join('')}
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Махалля *</label>
            <select name="mahalla" id="mahalla-select" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" disabled>
              <option value="">Сначала выберите район...</option>
            </select>
          </div>
        </div>

        <!-- Building Details -->
        <div class="space-y-4">
          <h4 class="font-medium text-gray-700 dark:text-gray-300">Детали здания</h4>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Тип здания</label>
              <select name="bino_turi" class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
                <option value="Yangi_qurilgan_uylar">Новостройка</option>
                <option value="Ikkinchi bozor" selected>Вторичный рынок</option>
                <option value="Stalin">Сталинка</option>
                <option value="Brezhnevka">Брежневка</option>
              </select>
            </div>
            <div>
              <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Тип строения</label>
              <select name="qurilish_turi" class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
                <option value="Panel" selected>Панельный</option>
                <option value="Monolitli">Монолитный</option>
                <option value="G'ishtli">Кирпичный</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
                        <div>
              <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Планировка</label>
              <select name="planirovka" class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
                <option value="Oddiy" selected>Обычная</option>
                <option value="Alohida">Раздельная</option>
                <option value="Studio">Студия</option>
              </select>
                        </div>
                         <div>
              <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Ремонт</label>
              <select name="renovation" class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
                <option value="Yaxshi" selected>Хороший</option>
                <option value="O'rta">Средний</option>
                <option value="Yomon">Плохой</option>
                <option value="Evroremont">Евроремонт</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Санузел</label>
              <select name="sanuzel" class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
                <option value="Birgalikda" selected>Совмещенный</option>
                <option value="Alohida">Раздельный</option>
              </select>
                        </div>
                        <div>
              <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Собственность</label>
              <select name="owner" class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
                <option value="Mulkdor" selected>Собственник</option>
                <option value="Xususiy">Частная</option>
                <option value="Ijara">Аренда</option>
              </select>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Мебель</label>
              <select name="mebel" class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
                <option value="Yo'q" selected>Нет</option>
                <option value="Ha">Есть</option>
                <option value="Qisman">Частично</option>
              </select>
                        </div>
                        <div>
              <label class="block text-sm text-gray-600 dark:text-gray-400 mb-1">Можно договориться</label>
              <select name="kelishsa" class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
                <option value="Ha" selected>Да</option>
                <option value="Yo'q">Нет</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Additional Features -->
        <div class="space-y-4">
          <h4 class="font-medium text-gray-700 dark:text-gray-300">Дополнительные удобства</h4>
          
          <div>
            <label class="block text-sm text-gray-600 dark:text-gray-400 mb-2">В доме (можно выбрать несколько)</label>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <label class="flex items-center"><input type="checkbox" name="uyda" value="Televizor" class="mr-2"> Телевизор</label>
              <label class="flex items-center"><input type="checkbox" name="uyda" value="Internet" checked class="mr-2"> Интернет</label>
              <label class="flex items-center"><input type="checkbox" name="uyda" value="Konditsioner" class="mr-2"> Кондиционер</label>
              <label class="flex items-center"><input type="checkbox" name="uyda" value="Telefon" class="mr-2"> Телефон</label>
              <label class="flex items-center"><input type="checkbox" name="uyda" value="Balkon" class="mr-2"> Балкон</label>
              <label class="flex items-center"><input type="checkbox" name="uyda" value="Lift" class="mr-2"> Лифт</label>
            </div>
          </div>

          <div>
            <label class="block text-sm text-gray-600 dark:text-gray-400 mb-2">Рядом с домом (можно выбрать несколько)</label>
            <div class="grid grid-cols-2 gap-2 text-sm">
              <label class="flex items-center"><input type="checkbox" name="atrofda" value="Maktab" checked class="mr-2"> Школа</label>
              <label class="flex items-center"><input type="checkbox" name="atrofda" value="Park" checked class="mr-2"> Парк</label>
              <label class="flex items-center"><input type="checkbox" name="atrofda" value="Shifoxona" class="mr-2"> Больница</label>
              <label class="flex items-center"><input type="checkbox" name="atrofda" value="Do'kon" class="mr-2"> Магазин</label>
              <label class="flex items-center"><input type="checkbox" name="atrofda" value="Metro" class="mr-2"> Метро</label>
              <label class="flex items-center"><input type="checkbox" name="atrofda" value="Avtobus" class="mr-2"> Автобус</label>
            </div>
          </div>
                        </div>

        <div class="flex gap-2 pt-4">
          <button type="button" id="evaluate-first-btn" class="flex-1 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition">
            <i data-lucide="calculator" class="mr-2 h-4 w-4 inline"></i>
            Сначала оценить
          </button>
          <button type="submit" class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
            Добавить актив
          </button>
                        </div>
                    </form>
    `;
    
    // After setting the HTML, add event listener for district change
    setTimeout(() => {
      const districtSelect = document.getElementById('district-select');
      const mahallaSelect = document.getElementById('mahalla-select');
      
      if (districtSelect && mahallaSelect) {
        districtSelect.addEventListener('change', function() {
          const selectedDistrict = this.value;
          mahallaSelect.innerHTML = '<option value="">Выберите махаллю...</option>';
          
          if (selectedDistrict && districtMahallas[selectedDistrict]) {
            mahallaSelect.disabled = false;
            districtMahallas[selectedDistrict].forEach(mahalla => {
              const option = document.createElement('option');
              option.value = mahalla;
              option.textContent = mahalla;
              mahallaSelect.appendChild(option);
            });
          } else {
            mahallaSelect.disabled = true;
            mahallaSelect.innerHTML = '<option value="">Сначала выберите район...</option>';
          }
        });
      }
      
      // Add event listener for "Evaluate First" button
      const evaluateBtn = document.getElementById('evaluate-first-btn');
      if (evaluateBtn) {
        evaluateBtn.addEventListener('click', async function() {
          const form = document.getElementById('add-asset-form');
          const formData = new FormData(form);
          const data = Object.fromEntries(formData.entries());
          
          // Show loading state
          const originalText = this.textContent;
          this.disabled = true;
          this.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-4 w-4 inline animate-spin"></i>Оценка...';
          lucide.createIcons();
          
          try {
            // Get checkboxes values
            const uydaCheckboxes = Array.from(document.querySelectorAll('input[name="uyda"]:checked')).map(cb => cb.value);
            const atrofdaCheckboxes = Array.from(document.querySelectorAll('input[name="atrofda"]:checked')).map(cb => cb.value);
            
            const evaluationData = {
              rooms: parseInt(data.rooms),
              floor: parseInt(data.floor),
              total_floors: parseInt(data.total_floors),
              area: parseInt(data.area),
              month: new Date().getMonth() + 1,
              year: new Date().getFullYear(),
              kelishsa: data.kelishsa || "Ha",
              mebel: data.mebel || "Yo'q",
              district: data.district,
              mahalla: data.mahalla,
              atrofda: atrofdaCheckboxes.length > 0 ? atrofdaCheckboxes : ["Maktab", "Park"],
              uyda: uydaCheckboxes.length > 0 ? uydaCheckboxes : ["Televizor", "Internet"],
              bino_turi: data.bino_turi || "Ikkinchi bozor",
              qurilish_turi: data.qurilish_turi || "Panel",
              renovation: data.renovation || "Yaxshi",
              owner: data.owner || "Mulkdor",
              sanuzel: data.sanuzel || "Birgalikda",
              planirovka: data.planirovka || "Oddiy"
            };
            
            console.log('Evaluating apartment with data:', evaluationData);
            
            const evaluation = await evaluateApartment(evaluationData);
            
            if (evaluation && evaluation.predicted_price) {
              alert(`Расчетная стоимость квартиры: $${evaluation.predicted_price.toLocaleString('en-US', {maximumFractionDigits: 0})}`);
            } else {
              alert('Не удалось выполнить оценку. Проверьте введенные данные.');
            }
            
          } catch (error) {
            console.error('Error evaluating apartment:', error);
            alert('Произошла ошибка при оценке квартиры. Попробуйте еще раз.');
          } finally {
            // Reset button
            this.disabled = false;
            this.innerHTML = originalText;
            lucide.createIcons();
          }
        });
      }
    }, 100);
  } else if (assetType === 'car') {
    formHtml = `
                    <h3 class="text-2xl font-bold mb-6">Параметры автомобиля</h3>
                    <form id="add-asset-form" class="space-y-4">
        <input type="hidden" name="asset_type" value="car">
        
        <!-- Asset Basic Info -->
                        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Название актива</label>
          <input type="text" name="name" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" placeholder="Например: Toyota Camry 2022">
                        </div>

        <!-- Portfolio Selection -->
                         <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Портфель</label>
          <select name="portfolio_id" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
            <option value="">Выберите портфель...</option>
            ${portfolios.map(portfolio => `<option value="${portfolio.id}">${portfolio.name}</option>`).join('')}
          </select>
                        </div>

        <!-- State Selection -->
                        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Регион</label>
          <select name="state" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
            <option value="">Выберите регион...</option>
            <option value="Toshkent shahri">Ташкент город</option>
            <option value="Qoraqalpogʻiston Respublikasi">Каракалпакстан</option>
            <option value="Navoiy Viloyati">Навоийская область</option>
            <option value="Toshkent Viloyati">Ташкентская область</option>
            <option value="Samarqand Viloyati">Самаркандская область</option>
            <option value="Qashqadaryo Viloyati">Кашкадарьинская область</option>
            <option value="Farg'ona Viloyati">Ферганская область</option>
            <option value="Buxoro Viloyati">Бухарская область</option>
            <option value="Xorazm Viloyati">Хорезмская область</option>
            <option value="Sirdaryo Viloyati">Сырдарьинская область</option>
            <option value="Surxondaryo Viloyati">Сурхандарьинская область</option>
            <option value="Namangan Viloyati">Наманганская область</option>
            <option value="Andijon Viloyati">Андижанская область</option>
            <option value="Jizzax Viloyati">Джизакская область</option>
          </select>
                        </div>

        <!-- Car Brand and Model -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Марка</label>
            <select name="brand" id="car-brand-select" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
              <option value="">Выберите марку...</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Модель</label>
            <select name="model" id="car-model-select" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" disabled>
              <option value="">Сначала выберите марку...</option>
            </select>
          </div>
        </div>

        <!-- Year and Engine Volume -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Год выпуска</label>
            <input type="number" name="year" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" min="1980" max="2025" value="2020">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Объем двигателя (л)</label>
            <input type="number" name="engine_volume" id="engine-volume-input" step="0.1" min="0.8" max="8.0" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
          </div>
        </div>

        <!-- Fuel Type -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Тип топлива</label>
          <select name="fuel" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
            <option value="">Выберите тип топлива...</option>
            <option value="Benzin">Бензин</option>
            <option value="Gaz/Benzin">Газ/Бензин</option>
            <option value="Gibrid">Гибрид</option>
            <option value="Dizel">Дизель</option>
            <option value="Elektro">Электро</option>
            <option value="Boshqa">Другое</option>
          </select>
        </div>

        <!-- Ownership and Body Type -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Тип собственности</label>
            <select name="ownership" class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
              <option value="Xususiy">Частная</option>
              <option value="Biznes">Бизнес</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Тип кузова</label>
            <select name="body_type" id="body-type-select" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
              <option value="">Выберите тип кузова...</option>
              <option value="Sedan">Седан</option>
              <option value="Xetchbek">Хэтчбек</option>
              <option value="Universal">Универсал</option>
              <option value="Yo'ltanlamas">Внедорожник</option>
              <option value="Kupe">Купе</option>
              <option value="Miniven">Минивэн</option>
              <option value="Pikap">Пикап</option>
              <option value="Kabriolet">Кабриолет</option>
              <option value="Boshqa">Другое</option>
            </select>
          </div>
        </div>

        <!-- Color and Condition -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Цвет</label>
            <select name="color" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
              <option value="">Выберите цвет...</option>
              <option value="Oq">Белый</option>
              <option value="Qora">Черный</option>
              <option value="Kulrang">Серый</option>
              <option value="Kumush">Серебристый</option>
              <option value="Ko'k">Синий</option>
              <option value="Jigarrang">Коричневый</option>
              <option value="Asfalt">Асфальт</option>
              <option value="Bejeviy">Бежевый</option>
              <option value="Boshqa">Другой</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Состояние</label>
            <select name="condition" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
              <option value="">Выберите состояние...</option>
              <option value="A'lo">Отличное</option>
              <option value="Yaxshi">Хорошее</option>
              <option value="O'rtacha">Среднее</option>
              <option value="Remont talab">Требует ремонта</option>
            </select>
          </div>
        </div>

        <!-- Owners Count and Mileage -->
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Количество владельцев</label>
            <select name="owners_count" class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4+</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Пробег (км)</label>
            <input type="number" name="mileage" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" min="0" placeholder="100000">
          </div>
        </div>

        <!-- Transmission -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Коробка передач</label>
          <select name="transmission" class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg">
            <option value="Mexanik">Механическая</option>
            <option value="Avtomat">Автоматическая</option>
          </select>
        </div>

        <!-- Features -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Дополнительные опции</label>
          <div class="grid grid-cols-2 gap-2">
            <label class="flex items-center">
              <input type="checkbox" name="features" value="Konditsioner" class="mr-2">
              <span class="text-sm">Кондиционер</span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" name="features" value="Xavfsizlik tizimi" class="mr-2">
              <span class="text-sm">Система безопасности</span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" name="features" value="Parctronik" class="mr-2">
              <span class="text-sm">Парктроник</span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" name="features" value="Rastamojka qilingan" class="mr-2">
              <span class="text-sm">Растаможен</span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" name="features" value="Elektron oynalar" class="mr-2">
              <span class="text-sm">Электростеклоподъемники</span>
            </label>
            <label class="flex items-center">
              <input type="checkbox" name="features" value="Elektron ko'zgular" class="mr-2">
              <span class="text-sm">Электрозеркала</span>
            </label>
          </div>
        </div>

        <!-- Current Value -->
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Текущая стоимость ($)</label>
          <input type="number" name="current_value" required class="w-full p-2 bg-gray-50 dark:bg-gray-700 border dark:border-gray-600 rounded-lg" min="1000" placeholder="Оценочная стоимость">
          <p class="text-xs text-gray-500 mt-1">Используйте кнопку "Сначала оценить" для автоматической оценки</p>
        </div>

        <div class="pt-4 flex space-x-4">
          <button type="button" id="evaluate-car-btn" class="flex-1 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition">
            <i data-lucide="calculator" class="mr-2 h-4 w-4 inline"></i>Сначала оценить
          </button>
          <button type="submit" class="flex-1 bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition">
            <i data-lucide="plus" class="mr-2 h-4 w-4 inline"></i>Добавить автомобиль
          </button>
                        </div>
                    </form>
    `;
    
    // Load car brands after creating the form
    setTimeout(async () => {
      await loadCarBrands();
      initializeCarFormHandlers();
    }, 100);
  }
  step2.innerHTML = formHtml
  document.getElementById('wizard-step-1').classList.add('hidden')
  step2.classList.remove('hidden')

  // Add form submission listener
  document.getElementById('add-asset-form').addEventListener('submit', handleAddAsset)
  
  // Add evaluate button listener for apartments
  if (assetType === 'apartment') {
    const evaluateBtn = document.getElementById('evaluate-first-btn');
    if (evaluateBtn) {
      evaluateBtn.addEventListener('click', async () => {
        const form = document.getElementById('add-asset-form');
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        if (data.area && data.rooms && data.floor && data.total_floors) {
          evaluateBtn.disabled = true;
          evaluateBtn.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-4 w-4 inline animate-spin"></i>Оценка...';
          lucide.createIcons();
          
          try {
            // Get checkboxes values
            const uydaCheckboxes = Array.from(document.querySelectorAll('input[name="uyda"]:checked')).map(cb => cb.value);
            const atrofdaCheckboxes = Array.from(document.querySelectorAll('input[name="atrofda"]:checked')).map(cb => cb.value);
            
            const evaluationData = {
              rooms: parseInt(data.rooms),
              floor: parseInt(data.floor),
              total_floors: parseInt(data.total_floors),
              area: parseInt(data.area),
              month: new Date().getMonth() + 1,
              year: new Date().getFullYear(),
              kelishsa: data.kelishsa || "Ha",
              mebel: data.mebel || "Yo'q",
              district: data.district,
              mahalla: data.mahalla,
              atrofda: atrofdaCheckboxes.length > 0 ? atrofdaCheckboxes : ["Maktab", "Park"],
              uyda: uydaCheckboxes.length > 0 ? uydaCheckboxes : ["Televizor", "Internet"],
              bino_turi: data.bino_turi || "Ikkinchi bozor",
              qurilish_turi: data.qurilish_turi || "Panel",
              renovation: data.renovation || "Yaxshi",
              owner: data.owner || "Mulkdor",
              sanuzel: data.sanuzel || "Birgalikda",
              planirovka: data.planirovka || "Oddiy"
            };
            
            console.log('Apartment evaluation data:', evaluationData);
            
            const evaluation = await evaluateApartment(evaluationData);
            if (evaluation && evaluation.predicted_price) {
              alert(`Расчетная стоимость квартиры: $${evaluation.predicted_price.toLocaleString('en-US', {maximumFractionDigits: 0})}`);
            } else {
              alert('Не удалось выполнить оценку. Проверьте введенные данные.');
            }
          } catch (error) {
            console.error('Error evaluating apartment:', error);
            alert('Произошла ошибка при оценке квартиры. Попробуйте еще раз.');
          } finally {
            evaluateBtn.disabled = false;
            evaluateBtn.innerHTML = '<i data-lucide="calculator" class="mr-2 h-4 w-4 inline"></i>Сначала оценить';
            lucide.createIcons();
          }
        } else {
          alert('Пожалуйста, заполните все основные поля для оценки.');
        }
      });
    }
  }
  
  // Add create portfolio button listener
  const createPortfolioBtn = document.getElementById('create-portfolio-btn');
  if (createPortfolioBtn) {
    createPortfolioBtn.addEventListener('click', async () => {
      const portfolioName = prompt('Введите название портфеля:');
      if (portfolioName) {
        try {
          const response = await apiCall('/portfolios/', {
            method: 'POST',
            body: JSON.stringify({
              name: portfolioName,
              description: `Портфель: ${portfolioName}`
            })
          });
          
          if (response && response.ok) {
            const newPortfolio = await response.json();
            portfolios.push(newPortfolio);
            
            // Update the select dropdown
            const select = document.querySelector('select[name="portfolio_id"]');
            const option = document.createElement('option');
            option.value = newPortfolio.id;
            option.textContent = newPortfolio.name;
            option.selected = true;
            select.appendChild(option);
          }
        } catch (error) {
          console.error('Error creating portfolio:', error);
          alert('Не удалось создать портфель. Попробуйте еще раз.');
        }
      }
    });
  }
  
  // Reinitialize icons
  lucide.createIcons();
}

// --- NAVIGATION ---
function navigateTo(view, id = null) {
  currentView = view
  selectedAssetId = id

  // Clear all sidebar navigation items first (universal clearing)
  document.querySelectorAll('.sidebar-link').forEach(link => {
    link.classList.remove('active')
  })

  // Hide all views
  dashboardView.classList.add('hidden')
  assetDetailView.classList.add('hidden')
  addAssetView.classList.add('hidden')
  
  // Check if evaluate view exists and hide it
  const evaluateView = document.getElementById('evaluate-view')
  if (evaluateView) {
    evaluateView.classList.add('hidden')
  }

  // Check if market view exists and hide it
  const marketView = document.getElementById('market-view')
  if (marketView) {
    marketView.classList.add('hidden')
  }

  // Check if update evaluation view exists and hide it
  const updateEvaluationView = document.getElementById('update-evaluation-view')
  if (updateEvaluationView) {
    updateEvaluationView.classList.add('hidden')
  }

  // Show the correct view
  if (view === 'dashboard') {
    pageTitle.textContent = 'Мои Активы'
    dashboardView.classList.remove('hidden')
    backButton.classList.add('hidden')
    document.getElementById('nav-dashboard').classList.add('active')
    renderDashboard()
  } else if (view === 'asset-detail') {
    const asset = assets.find((a) => a.id === id)
    pageTitle.textContent = asset ? asset.name : 'Детали актива'
    assetDetailView.classList.remove('hidden')
    backButton.classList.remove('hidden')
    renderAssetDetail(id)
  } else if (view === 'add-asset') {
    pageTitle.textContent = 'Добавление нового актива'
    addAssetView.classList.remove('hidden')
    backButton.classList.remove('hidden')
    // Reset wizard to step 1
    document.getElementById('wizard-step-1').classList.remove('hidden')
    document.getElementById('wizard-step-2').classList.add('hidden')
  } else if (view === 'evaluate') {
    pageTitle.textContent = 'Оценить актив'
    if (evaluateView) {
      evaluateView.classList.remove('hidden')
    }
    backButton.classList.remove('hidden')
    
    // Set evaluate nav as active (sidebar clearing already done above)
    const navEvaluate = document.getElementById('nav-evaluate')
    if (navEvaluate) {
      navEvaluate.classList.add('active')
    }
    
    // Reset evaluate wizard to step 1
    const evaluateStep1 = document.getElementById('evaluate-step-1')
    const evaluateStep2 = document.getElementById('evaluate-step-2')
    const evaluateResult = document.getElementById('evaluate-result')
    
    if (evaluateStep1) evaluateStep1.classList.remove('hidden')
    if (evaluateStep2) evaluateStep2.classList.add('hidden')
    if (evaluateResult) evaluateResult.classList.add('hidden')
  } else if (view === 'market') {
    pageTitle.textContent = 'Аналитика рынка'
    const marketView = document.getElementById('market-view')
    if (marketView) {
      marketView.classList.remove('hidden')
    }
    backButton.classList.remove('hidden')
    
    // Set market nav as active (sidebar clearing already done above)
    const navMarket = document.getElementById('nav-market')
    if (navMarket) {
      navMarket.classList.add('active')
    }
    
    // Reset market view to selection screen
    const marketSelection = document.getElementById('market-selection')
    const marketDashboard = document.getElementById('market-dashboard')
    
    if (marketSelection) marketSelection.classList.remove('hidden')
    if (marketDashboard) marketDashboard.classList.add('hidden')
    
    // Initialize market event handlers
    initializeMarketHandlers()
  } else if (view === 'announcements') {
    pageTitle.textContent = 'Объявления'
    const announcementsView = document.getElementById('announcements-view')
    if (announcementsView) {
      announcementsView.classList.remove('hidden')
    }
    backButton.classList.remove('hidden')
    
    // Set announcements nav as active
    const navAnnouncements = document.getElementById('nav-announcements')
    if (navAnnouncements) {
      navAnnouncements.classList.add('active')
    }
    
    // Initialize marketplace functionality
    initializeMarketplace()
  } else if (view === 'ai-assistant') {
    pageTitle.textContent = 'AI Ассистент';
    const aiAssistantView = document.getElementById('ai-assistant-view');
    if (aiAssistantView) {
      aiAssistantView.classList.remove('hidden');
    }
    backButton.classList.remove('hidden');
    // Set AI Assistant nav as active
    const navAiAssistant = document.getElementById('nav-ai-assistant');
    if (navAiAssistant) {
      navAiAssistant.classList.add('active');
    }
  }
  
  // Hide announcements view when navigating away
  const announcementsView = document.getElementById('announcements-view')
  if (announcementsView && view !== 'announcements') {
    announcementsView.classList.add('hidden')
  }
  
  // Hide AI Assistant view when navigating away
  const aiAssistantView = document.getElementById('ai-assistant-view')
  if (aiAssistantView && view !== 'ai-assistant') {
    aiAssistantView.classList.add('hidden')
  }
  
  lucide.createIcons()
}

// --- EVENT HANDLERS ---

async function handleAddAsset(event) {
  event.preventDefault()
  const formData = new FormData(event.target)
  const data = Object.fromEntries(formData.entries())

  // Show loading state
  const submitBtn = event.target.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-4 w-4 inline animate-spin"></i>Добавление...';
  lucide.createIcons();

  try {
    let assetData = {
      name: data.name,
      asset_type: data.asset_type,
      address: data.asset_type === 'car' ? 'Автомобиль (без фиксированного адреса)' : (data.location || ''),
      portfolio: data.portfolio_id
    };

    if (data.asset_type === 'apartment') {
      // For apartments, we can optionally evaluate first
      if (data.district && data.mahalla && data.area && data.rooms) {
        try {
          // Get checkboxes values for uyda and atrofda
          const uydaCheckboxes = Array.from(document.querySelectorAll('input[name="uyda"]:checked')).map(cb => cb.value);
          const atrofdaCheckboxes = Array.from(document.querySelectorAll('input[name="atrofda"]:checked')).map(cb => cb.value);
          
          const evaluationData = {
            rooms: parseInt(data.rooms),
            floor: parseInt(data.floor),
            total_floors: parseInt(data.total_floors),
            area: parseInt(data.area),
            month: new Date().getMonth() + 1,
            year: new Date().getFullYear(),
            kelishsa: data.kelishsa || "Ha",
            mebel: data.mebel || "Yo'q",
            district: data.district,
            mahalla: data.mahalla,
            atrofda: atrofdaCheckboxes.length > 0 ? atrofdaCheckboxes : ["Maktab", "Park"],
            uyda: uydaCheckboxes.length > 0 ? uydaCheckboxes : ["Televizor", "Internet"],
            bino_turi: data.bino_turi || "Ikkinchi bozor",
            qurilish_turi: data.qurilish_turi || "Panel",
            renovation: data.renovation || "Yaxshi",
            owner: data.owner || "Mulkdor",
            sanuzel: data.sanuzel || "Birgalikda",
            planirovka: data.planirovka || "Oddiy"
          };
          
          console.log('Apartment evaluation data:', evaluationData);
          
          const evaluation = await evaluateApartment(evaluationData);
          if (evaluation && evaluation.predicted_price) {
            assetData.current_value = evaluation.predicted_price;
          }
        } catch (error) {
          console.warn('Evaluation failed, using manual value:', error);
        }
      }

      // If no evaluation, use a mock value or require manual input
      if (!assetData.current_value) {
        assetData.current_value = data.area * 1000; // Mock calculation
      }

      // Add apartment-specific fields to the asset data
      assetData.area = parseFloat(data.area);
      assetData.rooms = parseInt(data.rooms);
      assetData.floor = parseInt(data.floor);
      assetData.total_floors = parseInt(data.total_floors);
      
      // Store additional details in description field
      const uydaChecked = Array.from(document.querySelectorAll('input[name="uyda"]:checked')).map(cb => cb.value);
      const atrofdaChecked = Array.from(document.querySelectorAll('input[name="atrofda"]:checked')).map(cb => cb.value);
      
      assetData.description = JSON.stringify({
        'Район': data.district || 'Не указан',
        'Махалля': data.mahalla || 'Не указана',
        'Тип здания': data.bino_turi || 'Не указан',
        'Тип строения': data.qurilish_turi || 'Не указан',
        'Планировка': data.planirovka || 'Не указана',
        'Ремонт': data.renovation || 'Не указан',
        'Санузел': data.sanuzel || 'Не указан',
        'Собственность': data.owner || 'Не указан',
        'Мебель': data.mebel || 'Не указана',
        'Можно договориться': data.kelishsa || 'Не указано',
        'В доме': uydaChecked.length > 0 ? uydaChecked.join(', ') : 'Не указано',
        'Рядом с домом': atrofdaChecked.length > 0 ? atrofdaChecked.join(', ') : 'Не указано'
      });

    } else if (data.asset_type === 'car') {
      assetData.current_value = parseFloat(data.current_value);
      assetData.brand = data.brand;
      assetData.model = data.model;
      assetData.year = parseInt(data.year);
      assetData.mileage = parseInt(data.mileage);
      
      // Get selected features
      const featuresCheckboxes = Array.from(document.querySelectorAll('input[name="features"]:checked')).map(cb => cb.value);
      
      assetData.description = JSON.stringify({
        'Регион': data.state,
        'Марка': data.brand,
        'Модель': data.model,
        'Год выпуска': data.year,
        'Объем двигателя': `${data.engine_volume} л`,
        'Топливо': data.fuel,
        'Тип собственности': data.ownership || 'Частная',
        'Тип кузова': data.body_type,
        'Цвет': data.color,
        'Состояние': data.condition,
        'Владельцев': data.owners_count || '1',
        'Пробег': `${data.mileage} км`,
        'Коробка передач': data.transmission || 'Механическая',
        'Опции': featuresCheckboxes.length > 0 ? featuresCheckboxes.join(', ') : 'Не указаны'
      });
    }

    // Log the final asset data being sent
    console.log('Final asset data being sent:', assetData);
    
    // Create the asset
    const newAsset = await createAsset(assetData);
    
    if (newAsset) {
      // Add to local assets array
      assets.push(newAsset);
      
      // Reload dashboard data
      await loadAppData();
      
      // Navigate back to dashboard
      navigateTo('dashboard');
      
      // Show success message
      console.log('Asset added successfully:', newAsset);
    } else {
      throw new Error('Failed to create asset');
    }

  } catch (error) {
    console.error('Error adding asset:', error);
    alert('Произошла ошибка при добавлении актива. Попробуйте еще раз.');
    
    // Reset button
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
  }
}

async function createDefaultPortfolio() {
  try {
    const response = await apiCall('/portfolios/', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Мой портфель',
        description: 'Основной портфель активов'
      })
    });
    
    if (response && response.ok) {
      const portfolio = await response.json();
      portfolios.push(portfolio);
      return portfolio;
    }
    return null;
  } catch (error) {
    console.error('Error creating default portfolio:', error);
    return null;
  }
}

function toggleMenu() {
  const aside = document.getElementById('aside')
  aside.classList.toggle('mobile')
  const profile = document.getElementById('profile')
  profile.classList.toggle('mobile')
}

document.getElementById('mobile-close').addEventListener('click', (e) => {
  toggleMenu()
})

document.getElementById('nav-dashboard').addEventListener('click', (e) => {
  e.preventDefault()
  navigateTo('dashboard')
})

document.getElementById('back-button').addEventListener('click', (e) => {
  e.preventDefault()
  if (
    currentView === 'add-asset' &&
    !document.getElementById('wizard-step-1').classList.contains('hidden')
  ) {
    navigateTo('dashboard')
  } else if (currentView === 'add-asset') {
    // Go back to step 1 in wizard
    document.getElementById('wizard-step-1').classList.remove('hidden')
    document.getElementById('wizard-step-2').classList.add('hidden')
  } else {
    navigateTo('dashboard')
  }
})

document.getElementById('add-asset-btn-header').addEventListener('click', () => {
  navigateTo('add-asset')
})

document.querySelectorAll('.wizard-asset-type-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    const assetType = btn.dataset.assetType
    renderAddAssetForm(assetType)
  })
})

// --- INITIALIZATION ---
window.onload = () => {
  initApp()
}

// Car evaluation functions
let carBrands = [];
let carModels = [];

async function loadCarBrands() {
  try {
    const response = await apiCall('/car-brands/');
    if (response && response.ok) {
      const data = await response.json();
      carBrands = data.brands || [];
      
      const brandSelect = document.getElementById('car-brand-select');
      if (brandSelect) {
        brandSelect.innerHTML = '<option value="">Выберите марку...</option>';
        carBrands.forEach(brand => {
          const option = document.createElement('option');
          option.value = brand;
          option.textContent = brand;
          brandSelect.appendChild(option);
        });
      }
    }
  } catch (error) {
    console.error('Error loading car brands:', error);
  }
}

async function loadCarModels(brand) {
  try {
    const response = await apiCall(`/car-models/?brand=${encodeURIComponent(brand)}`);
    if (response && response.ok) {
      const data = await response.json();
      carModels = data.models || [];
      
      const modelSelect = document.getElementById('car-model-select');
      if (modelSelect) {
        modelSelect.innerHTML = '<option value="">Выберите модель...</option>';
        carModels.forEach(model => {
          const option = document.createElement('option');
          option.value = model;
          option.textContent = model.replace(/_/g, ' ');
          modelSelect.appendChild(option);
        });
        modelSelect.disabled = false;
      }
    }
  } catch (error) {
    console.error('Error loading car models:', error);
  }
}

async function loadCarSpecs(model) {
  try {
    const response = await apiCall(`/car-specs/?model=${encodeURIComponent(model)}`);
    if (response && response.ok) {
      const data = await response.json();
      
      const bodyTypeSelect = document.getElementById('body-type-select');
      const engineVolumeInput = document.getElementById('engine-volume-input');
      
      if (data.body_type && bodyTypeSelect) {
        bodyTypeSelect.value = data.body_type;
      }
      
      if (data.engine_volume && engineVolumeInput) {
        engineVolumeInput.value = data.engine_volume;
      }
    }
  } catch (error) {
    console.error('Error loading car specs:', error);
  }
}

async function evaluateCar(carData) {
  try {
    const response = await apiCall('/evaluate-car/', {
      method: 'POST',
      body: JSON.stringify(carData)
    });
    if (response && response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error('Error evaluating car:', error);
    throw error;
  }
}

function initializeCarFormHandlers() {
  // Brand selection handler
  const brandSelect = document.getElementById('car-brand-select');
  if (brandSelect) {
    brandSelect.addEventListener('change', async function() {
      const selectedBrand = this.value;
      const modelSelect = document.getElementById('car-model-select');
      
      if (selectedBrand) {
        await loadCarModels(selectedBrand);
      } else {
        modelSelect.innerHTML = '<option value="">Сначала выберите марку...</option>';
        modelSelect.disabled = true;
      }
    });
  }
  
  // Model selection handler
  const modelSelect = document.getElementById('car-model-select');
  if (modelSelect) {
    modelSelect.addEventListener('change', async function() {
      const selectedModel = this.value;
      
      if (selectedModel) {
        await loadCarSpecs(selectedModel);
      }
    });
  }
  
  // Car evaluation button handler
  const evaluateCarBtn = document.getElementById('evaluate-car-btn');
  if (evaluateCarBtn) {
    evaluateCarBtn.addEventListener('click', async function() {
      const form = document.getElementById('add-asset-form');
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());
      
      // Get selected features
      const featuresCheckboxes = Array.from(document.querySelectorAll('input[name="features"]:checked')).map(cb => cb.value);
      
      // Validate required fields
      const requiredFields = ['state', 'brand', 'model', 'year', 'engine_volume', 'fuel', 'body_type', 'color', 'condition', 'mileage'];
      const missingFields = requiredFields.filter(field => !data[field]);
      
      if (missingFields.length > 0) {
        alert(`Пожалуйста, заполните все обязательные поля: ${missingFields.join(', ')}`);
        return;
      }
      
      // Show loading state
      const originalText = this.textContent;
      this.disabled = true;
      this.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-4 w-4 inline animate-spin"></i>Оценка...';
      lucide.createIcons();
      
      try {
        const evaluationData = {
          brand: data.brand,
          model: data.model,
          year: parseInt(data.year),
          engine_volume: parseFloat(data.engine_volume),
          fuel: data.fuel,
          transmission: data.transmission || "Mexanik",
          body_type: data.body_type,
          mileage: parseInt(data.mileage),
          color: data.color || "Oq",
          condition: data.condition || "Yaxshi",
          state: data.state,
          ownership: data.ownership || "Xususiy",
          owners_count: parseInt(data.owners_count) || 1,
          features: featuresCheckboxes,
          month: new Date().getMonth() + 1
        };
        
        console.log('Evaluating car with data:', evaluationData);
        
        const evaluation = await evaluateCar(evaluationData);
        
        if (evaluation && evaluation.predicted_price) {
          alert(`Расчетная стоимость автомобиля: ${evaluation.formatted_price}\nДиапазон цен: ${evaluation.formatted_range}`);
          
          // Auto-fill the current value field if it exists
          const currentValueInput = document.querySelector('input[name="current_value"]');
          if (currentValueInput) {
            currentValueInput.value = evaluation.predicted_price;
          }
        } else {
          alert('Не удалось выполнить оценку. Проверьте введенные данные.');
        }
        
      } catch (error) {
        console.error('Error evaluating car:', error);
        alert('Произошла ошибка при оценке автомобиля. Попробуйте еще раз.');
      } finally {
        // Reset button
        this.disabled = false;
        this.innerHTML = originalText;
        lucide.createIcons();
      }
    });
  }
}

async function loadUserProfile() {
  try {
    const response = await apiCall('/auth/profile/');
    if (response && response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error('Error loading user profile:', error);
    return null;
  }
}

function updateUserAvatar(userData) {
  const avatarElement = document.querySelector('#profile img');
  if (avatarElement && userData) {
    let initials = 'П'; // Default initial in Russian
    
    // Priority 1: Use the actual name entered during registration (username field)
    if (userData.username && userData.username !== userData.email) {
      const nameParts = userData.username.split(/\s+/);
      if (nameParts.length >= 2) {
        initials = (nameParts[0].charAt(0) + nameParts[nameParts.length - 1].charAt(0)).toUpperCase();
      } else {
        initials = userData.username.charAt(0).toUpperCase();
      }
    }
    // Priority 2: Use first_name and last_name if available
    else if (userData.first_name || userData.last_name) {
      const firstName = userData.first_name || '';
      const lastName = userData.last_name || '';
      initials = (firstName.charAt(0) + lastName.charAt(0)).toUpperCase() || 'П';
    } 
    // Priority 3: Extract initials from email as fallback
    else if (userData.email) {
      const emailPrefix = userData.email.split('@')[0];
      const nameParts = emailPrefix.split(/[._-]/);
      if (nameParts.length >= 2) {
        initials = (nameParts[0].charAt(0) + nameParts[1].charAt(0)).toUpperCase();
      } else if (nameParts.length === 1) {
        initials = nameParts[0].charAt(0).toUpperCase();
      }
    }
    
    // Use a blue background with white text for the avatar
    avatarElement.src = `https://placehold.co/100x100/4F46E5/FFFFFF?text=${encodeURIComponent(initials)}`;
    avatarElement.alt = `User Avatar`;
  }
}

// --- EVALUATION FUNCTIONALITY ---

// Add evaluation navigation to existing event listeners
function addEvaluationNavigation() {
  // This function is no longer needed since evaluate navigation 
  // is handled by the main navigation system in initializeEventListeners()
}

// Update navigation to include evaluate view
function updateNavigationForEvaluate() {
  // Hide all views
  document.getElementById('dashboard-view').classList.add('hidden')
  document.getElementById('asset-detail-view').classList.add('hidden')
  document.getElementById('add-asset-view').classList.add('hidden')
  if (document.getElementById('evaluate-view')) {
    document.getElementById('evaluate-view').classList.add('hidden')
  }
  
  // Update sidebar
  document.querySelectorAll('.sidebar-link').forEach(link => {
    link.classList.remove('active')
  })
}

// Navigate to evaluate view
function navigateToEvaluate() {
  updateNavigationForEvaluate()
  document.getElementById('page-title').textContent = 'Оценить актив'
  document.getElementById('evaluate-view').classList.remove('hidden')
  document.getElementById('back-button').classList.remove('hidden')
  
  // Reset evaluate wizard to step 1
  document.getElementById('evaluate-step-1').classList.remove('hidden')
  document.getElementById('evaluate-step-2').classList.add('hidden')
  if (document.getElementById('evaluate-result')) {
    document.getElementById('evaluate-result').classList.add('hidden')
  }
  
  // Update sidebar navigation
  document.getElementById('nav-evaluate').classList.add('active')
  
  lucide.createIcons()
}

// Render evaluation form
function renderEvaluationForm(assetType) {
  const step1 = document.getElementById('evaluate-step-1')
  const step2 = document.getElementById('evaluate-step-2')
  
  step1.classList.add('hidden')
  step2.classList.remove('hidden')
  
  let formHtml = ''
  
  if (assetType === 'apartment') {
    formHtml = generateApartmentEvaluationForm()
  } else if (assetType === 'car') {
    formHtml = generateCarEvaluationForm()
  }
  
  step2.innerHTML = formHtml
  
  // Initialize form handlers after a small delay to ensure DOM is ready
  setTimeout(() => {
    if (assetType === 'apartment') {
      initializeApartmentEvaluationHandlers()
    } else if (assetType === 'car') {
      initializeCarEvaluationHandlers()
    }
    
    lucide.createIcons()
  }, 100)
}

// Generate apartment evaluation form
function generateApartmentEvaluationForm() {
  return `
    <div class="mb-6">
      <button 
        onclick="document.getElementById('evaluate-step-1').classList.remove('hidden'); document.getElementById('evaluate-step-2').classList.add('hidden')"
        class="flex items-center text-gray-600 dark:text-gray-300 hover:text-blue-600 mb-4"
      >
        <i data-lucide="arrow-left" class="mr-2"></i>
        Назад к выбору
      </button>
      <h3 class="text-2xl font-bold mb-8">Оценка квартиры</h3>
    </div>
    
    <form id="apartment-evaluation-form" class="space-y-6">
      <input type="hidden" name="asset_type" value="apartment" />
      
      <!-- District and Mahalla -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Район *</label>
          <select name="district" id="eval-district" required class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="">Выберите район</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Махалля *</label>
          <select name="mahalla" id="eval-mahalla" required class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="">Выберите махаллю</option>
          </select>
        </div>
      </div>
      
      <!-- Area and Rooms -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Площадь (м²) *</label>
          <input type="number" name="area" required min="1" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Количество комнат *</label>
          <input type="number" name="rooms" required min="1" max="10" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" />
        </div>
      </div>
      
      <!-- Floor and Total Floors -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Этаж *</label>
          <input type="number" name="floor" required min="1" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Этажность дома *</label>
          <input type="number" name="total_floors" required min="1" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" />
        </div>
      </div>
      
      <!-- Building Details -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Тип здания</label>
          <select name="bino_turi" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="Yangi_qurilgan_uylar">Новостройка</option>
            <option value="Ikkilamchi_bozor" selected>Вторичный рынок</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Материал строения</label>
          <select name="qurilish_turi" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="Panelli" selected>Панельный</option>
            <option value="Monolitli">Монолитный</option>
            <option value="G_ishtli">Кирпичный</option>
            <option value="Blokli">Блочный</option>
            <option value="Yog_ochli">Деревянный</option>
          </select>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Планировка</label>
          <select name="planirovka" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="Alohida_ajratilgan" selected>Раздельная</option>
            <option value="Aralash">Смешанная</option>
            <option value="Aralash_alohida">Смешанная раздельная</option>
            <option value="Kichik_oilalar_uchun">Для малых семей</option>
            <option value="Ko_p_darajali">Многоуровневая</option>
            <option value="Pentxaus">Пентхаус</option>
            <option value="Studiya">Студия</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Санузел</label>
          <select name="sanuzel" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="Alohida" selected>Раздельный</option>
            <option value="Aralash">Совмещенный</option>
            <option value="2_va_undan_ko_p_sanuzel">2 и более санузлов</option>
          </select>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Ремонт</label>
          <select name="renovation" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="Yaxshi" selected>Хороший</option>
            <option value="Zo_r">Отличный</option>
            <option value="Qoniqarsiz">Плохой</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Собственность</label>
          <select name="owner" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="Xususiy" selected>Частная</option>
            <option value="Biznes">Бизнес</option>
          </select>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Мебель</label>
          <select name="mebel" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="Yo'q" selected>Без мебели</option>
            <option value="Ha">С мебелью</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Можно торговаться</label>
          <select name="kelishsa" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="Yes" selected>Да</option>
            <option value="No">Нет</option>
          </select>
        </div>
      </div>
      
      <!-- Additional Features -->
      <div class="space-y-4">
        <h4 class="font-medium text-gray-700 dark:text-gray-300">Дополнительные удобства</h4>
        
        <div>
          <label class="block text-sm text-gray-600 dark:text-gray-400 mb-2">В квартире (можно выбрать несколько)</label>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <label class="flex items-center"><input type="checkbox" name="uyda" value="Televizor" class="mr-2"> Телевизор</label>
            <label class="flex items-center"><input type="checkbox" name="uyda" value="Internet" checked class="mr-2"> Интернет</label>
            <label class="flex items-center"><input type="checkbox" name="uyda" value="Konditsioner" class="mr-2"> Кондиционер</label>
            <label class="flex items-center"><input type="checkbox" name="uyda" value="Telefon" class="mr-2"> Телефон</label>
            <label class="flex items-center"><input type="checkbox" name="uyda" value="Balkon" class="mr-2"> Балкон</label>
            <label class="flex items-center"><input type="checkbox" name="uyda" value="Kir yuvish mashinasi" class="mr-2"> Стиральная машина</label>
            <label class="flex items-center"><input type="checkbox" name="uyda" value="Sovutgich" class="mr-2"> Холодильник</label>
            <label class="flex items-center"><input type="checkbox" name="uyda" value="Oshxona" class="mr-2"> Кухня</label>
            <label class="flex items-center"><input type="checkbox" name="uyda" value="Kabel TV" class="mr-2"> Кабельное ТВ</label>
          </div>
        </div>

        <div>
          <label class="block text-sm text-gray-600 dark:text-gray-400 mb-2">Рядом с домом (можно выбрать несколько)</label>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Maktab" checked class="mr-2"> Школа</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Park" checked class="mr-2"> Парк</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Shifoxona" class="mr-2"> Больница</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Supermarket" class="mr-2"> Супермаркет</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Do'kon" class="mr-2"> Магазин</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Avtoturargoh" class="mr-2"> Парковка</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Poliklinika" class="mr-2"> Поликлиника</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Bekat" class="mr-2"> Остановка</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Bolalar maydonchasi" class="mr-2"> Детская площадка</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Restoran" class="mr-2"> Ресторан</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Kafe" class="mr-2"> Кафе</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Ko'ngilochar maskanlar" class="mr-2"> Развлечения</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Bog'cha" class="mr-2"> Детский сад</label>
            <label class="flex items-center"><input type="checkbox" name="atrofda" value="Yashil hudud" class="mr-2"> Зеленая зона</label>
          </div>
        </div>
      </div>
      
      <div class="flex justify-center mt-8">
        <button 
          type="submit" 
          class="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition flex items-center"
        >
          <i data-lucide="calculator" class="mr-2 h-5 w-5"></i>
          Оценить
        </button>
      </div>
    </form>
  `
}

// Generate car evaluation form
function generateCarEvaluationForm() {
  return `
    <div class="mb-6">
      <button 
        onclick="document.getElementById('evaluate-step-1').classList.remove('hidden'); document.getElementById('evaluate-step-2').classList.add('hidden')"
        class="flex items-center text-gray-600 dark:text-gray-300 hover:text-blue-600 mb-4"
      >
        <i data-lucide="arrow-left" class="mr-2"></i>
        Назад к выбору
      </button>
      <h3 class="text-2xl font-bold mb-8">Оценка автомобиля</h3>
    </div>
    
    <form id="car-evaluation-form" class="space-y-6">
      <input type="hidden" name="asset_type" value="car" />
      
      <!-- Region -->
      <div>
        <label class="block text-sm font-medium mb-2">Регион</label>
        <select name="state" required class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
          <option value="">Выберите регион</option>
          <option value="Toshkent shahri">г. Ташкент</option>
          <option value="Toshkent Viloyati">Ташкентская область</option>
          <option value="Samarqand Viloyati">Самаркандская область</option>
          <option value="Buxoro Viloyati">Бухарская область</option>
          <option value="Andijon Viloyati">Андижанская область</option>
          <option value="Farg'ona Viloyati">Ферганская область</option>
          <option value="Namangan Viloyati">Наманганская область</option>
          <option value="Qashqadaryo Viloyati">Кашкадарьинская область</option>
          <option value="Surxondaryo Viloyati">Сурхандарьинская область</option>
          <option value="Jizzax Viloyati">Джизакская область</option>
          <option value="Sirdaryo Viloyati">Сырдарьинская область</option>
          <option value="Navoiy Viloyati">Навоийская область</option>
          <option value="Xorazm Viloyati">Хорезмская область</option>
          <option value="Qoraqalpogʻiston Respublikasi">Республика Каракалпакстан</option>
        </select>
      </div>
      
      <!-- Brand and Model -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Марка</label>
          <select name="brand" id="eval-car-brand" required class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="">Выберите марку</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Модель</label>
          <select name="model" id="eval-car-model" required class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="">Выберите модель</option>
          </select>
        </div>
      </div>
      
      <!-- Year and Engine -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Год выпуска</label>
          <input type="number" name="year" required min="1980" max="2025" value="2020" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Объем двигателя (л)</label>
          <input type="number" name="engine_volume" required step="0.1" min="0.5" max="8.0" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" />
        </div>
      </div>
      
      <!-- Additional fields -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Топливо</label>
          <select name="fuel" required class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="">Выберите топливо</option>
            <option value="Benzin">Бензин</option>
            <option value="Gaz/Benzin">Газ/Бензин</option>
            <option value="Dizel">Дизель</option>
            <option value="Gibrid">Гибрид</option>
            <option value="Elektro">Электро</option>
            <option value="Boshqa">Другое</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Коробка передач</label>
          <select name="transmission" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="Mexanik">Механическая</option>
            <option value="Avtomat">Автоматическая</option>
          </select>
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Тип кузова</label>
          <select name="body_type" required class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="">Выберите тип</option>
            <option value="Sedan">Седан</option>
            <option value="Xetchbek">Хэтчбек</option>
            <option value="Universal">Универсал</option>
            <option value="Yo'ltanlamas">Внедорожник</option>
            <option value="Kupe">Купе</option>
            <option value="Miniven">Минивэн</option>
            <option value="Pikap">Пикап</option>
            <option value="Kabriolet">Кабриолет</option>
            <option value="Boshqa">Другое</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Пробег (км)</label>
          <input type="number" name="mileage" required min="0" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700" />
        </div>
      </div>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Цвет</label>
          <select name="color" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="Oq">Белый</option>
            <option value="Qora">Черный</option>
            <option value="Kumush">Серебристый</option>
            <option value="Kulrang">Серый</option>
            <option value="Ko'k">Синий</option>
            <option value="Jigarrang">Коричневый</option>
            <option value="Bejeviy">Бежевый</option>
            <option value="Asfalt">Асфальт</option>
            <option value="Boshqa">Другой</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Состояние</label>
          <select name="condition" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="A'lo">Отличное</option>
            <option value="Yaxshi">Хорошее</option>
            <option value="O'rtacha">Среднее</option>
            <option value="Remont talab">Требует ремонта</option>
          </select>
        </div>
      </div>
      
      <!-- Ownership and Owners Count -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium mb-2">Тип собственности</label>
          <select name="ownership" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="Xususiy">Частная</option>
            <option value="Biznes">Бизнес</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-2">Количество владельцев</label>
          <select name="owners_count" class="w-full p-3 border dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700">
            <option value="1">1</option>
            <option value="2">2</option>
            <option value="3">3</option>
            <option value="4">4+</option>
          </select>
        </div>
      </div>
      
      <!-- Features -->
      <div>
        <label class="block text-sm font-medium mb-3">Дополнительные опции</label>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
          <label class="flex items-center">
            <input type="checkbox" name="features" value="Konditsioner" class="mr-2 rounded">
            <span class="text-sm">Кондиционер</span>
          </label>
          <label class="flex items-center">
            <input type="checkbox" name="features" value="Xavfsizlik tizimi" class="mr-2 rounded">
            <span class="text-sm">Система безопасности</span>
          </label>
          <label class="flex items-center">
            <input type="checkbox" name="features" value="Parctronik" class="mr-2 rounded">
            <span class="text-sm">Парктроник</span>
          </label>
          <label class="flex items-center">
            <input type="checkbox" name="features" value="Rastamojka qilingan" class="mr-2 rounded">
            <span class="text-sm">Растаможен</span>
          </label>
          <label class="flex items-center">
            <input type="checkbox" name="features" value="Elektron oynalar" class="mr-2 rounded">
            <span class="text-sm">Электростеклоподъемники</span>
          </label>
          <label class="flex items-center">
            <input type="checkbox" name="features" value="Elektron ko'zgular" class="mr-2 rounded">
            <span class="text-sm">Электрозеркала</span>
          </label>
        </div>
      </div>
      
      <div class="flex justify-center mt-8">
        <button 
          type="submit" 
          class="bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 transition flex items-center"
        >
          <i data-lucide="calculator" class="mr-2 h-5 w-5"></i>
          Оценить
        </button>
      </div>
    </form>
  `
}

// Initialize apartment evaluation handlers
function initializeApartmentEvaluationHandlers() {
  // Load districts
  loadDistrictsForEvaluation()
  
  // District change handler
  document.getElementById('eval-district').addEventListener('change', function() {
    const district = this.value
    const mahallaSelect = document.getElementById('eval-mahalla')
    
    if (district && districtMahallas[district]) {
      mahallaSelect.innerHTML = '<option value="">Выберите махаллю</option>'
      districtMahallas[district].forEach(mahalla => {
        const option = document.createElement('option')
        option.value = mahalla
        option.textContent = mahalla
        mahallaSelect.appendChild(option)
      })
      mahallaSelect.disabled = false
    } else {
      mahallaSelect.innerHTML = '<option value="">Выберите махаллю</option>'
      mahallaSelect.disabled = true
    }
  })
  
  // Form submission handler
  document.getElementById('apartment-evaluation-form').addEventListener('submit', async function(e) {
    e.preventDefault()
    await handleApartmentEvaluation(this)
  })
}

// Initialize car evaluation handlers
function initializeCarEvaluationHandlers() {
  // Load car brands
  loadCarBrandsForEvaluation()
  
  // Brand change handler
  document.getElementById('eval-car-brand').addEventListener('change', async function() {
    const brand = this.value
    if (brand) {
      await loadCarModelsForEvaluation(brand)
    }
  })
  
  // Model change handler
  document.getElementById('eval-car-model').addEventListener('change', async function() {
    const model = this.value
    if (model) {
      await loadCarSpecsForEvaluation(model)
    }
  })
  
  // Form submission handler
  document.getElementById('car-evaluation-form').addEventListener('submit', async function(e) {
    e.preventDefault()
    await handleCarEvaluation(this)
  })
}

// Load districts for evaluation
async function loadDistrictsForEvaluation() {
  const districtSelect = document.getElementById('eval-district')
  if (districtSelect) {
    districtSelect.innerHTML = '<option value="">Выберите район</option>'
    Object.keys(districtMahallas).forEach(district => {
      const option = document.createElement('option')
      option.value = district
      option.textContent = district
      districtSelect.appendChild(option)
    })
  }
}

// Load car brands for evaluation
async function loadCarBrandsForEvaluation() {
  console.log('DEBUG: Loading car brands for evaluation...')
  try {
    const response = await apiCall('/car-brands/')
    console.log('DEBUG: Car brands API response:', response)
    if (response && response.ok) {
      const data = await response.json()
      const brands = data.brands || []
      console.log('DEBUG: Car brands data:', brands)
      const brandSelect = document.getElementById('eval-car-brand')
      console.log('DEBUG: Brand select element found:', brandSelect)
      if (brandSelect) {
        brandSelect.innerHTML = '<option value="">Выберите марку</option>'
        brands.forEach(brand => {
          const option = document.createElement('option')
          option.value = brand
          option.textContent = brand
          brandSelect.appendChild(option)
        })
        console.log('DEBUG: Added', brands.length, 'brands to dropdown')
      } else {
        console.error('DEBUG: eval-car-brand element not found!')
      }
    } else {
      console.error('DEBUG: API response not ok:', response)
    }
  } catch (error) {
    console.error('Error loading car brands:', error)
  }
}

// Load car models for evaluation
async function loadCarModelsForEvaluation(brand) {
  try {
    const response = await apiCall(`/car-models/?brand=${encodeURIComponent(brand)}`)
    if (response && response.ok) {
      const data = await response.json()
      const models = data.models || []
      const modelSelect = document.getElementById('eval-car-model')
      if (modelSelect) {
        modelSelect.innerHTML = '<option value="">Выберите модель</option>'
        models.forEach(model => {
          const option = document.createElement('option')
          option.value = model
          option.textContent = model.replace(/_/g, ' ')
          modelSelect.appendChild(option)
        })
      }
    }
  } catch (error) {
    console.error('Error loading car models:', error)
  }
}

// Load car specs for evaluation
async function loadCarSpecsForEvaluation(model) {
  try {
    const response = await apiCall(`/car-specs/?model=${encodeURIComponent(model)}`)
    if (response && response.ok) {
      const specs = await response.json()
      if (specs.body_type) {
        const bodySelect = document.querySelector('select[name="body_type"]')
        if (bodySelect) {
          bodySelect.value = specs.body_type
        }
      }
      if (specs.engine_volume) {
        const engineInput = document.querySelector('input[name="engine_volume"]')
        if (engineInput) {
          engineInput.value = specs.engine_volume
        }
      }
    }
  } catch (error) {
    console.error('Error loading car specs:', error)
  }
}

// Handle apartment evaluation
async function handleApartmentEvaluation(form) {
  const submitBtn = form.querySelector('button[type="submit"]')
  const originalText = submitBtn.innerHTML
  
  try {
    // Show loading
    submitBtn.disabled = true
    submitBtn.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-4 w-4 inline animate-spin"></i>Оценка...'
    lucide.createIcons()
    
    // Get form data
    const formData = new FormData(form)
    const data = Object.fromEntries(formData.entries())
    
    // Get checkbox values
    const uydaElements = form.querySelectorAll('input[name="uyda"]:checked')
    const atrofdaElements = form.querySelectorAll('input[name="atrofda"]:checked')
    
    const uyda = Array.from(uydaElements).map(el => el.value)
    const atrofda = Array.from(atrofdaElements).map(el => el.value)
    
    // Prepare evaluation data
    const evaluationData = {
      rooms: parseInt(data.rooms),
      floor: parseInt(data.floor),
      total_floors: parseInt(data.total_floors),
      area: parseInt(data.area),
      month: new Date().getMonth() + 1,
      year: new Date().getFullYear(),
      kelishsa: data.kelishsa || "Yes",
      mebel: data.mebel || "Yo'q",
      district: data.district,
      mahalla: data.mahalla,
      atrofda: atrofda.length > 0 ? atrofda : ["Maktab", "Park"],
      uyda: uyda.length > 0 ? uyda : ["Internet"],
      bino_turi: data.bino_turi || "Ikkilamchi_bozor",
      qurilish_turi: data.qurilish_turi || "Panelli",
      renovation: data.renovation || "Yaxshi",
      owner: data.owner || "Xususiy",
      sanuzel: data.sanuzel || "Alohida",
      planirovka: data.planirovka || "Alohida_ajratilgan"
    }
    
    // Call evaluation API
    const result = await evaluateApartmentAPI(evaluationData)
    
    if (result) {
      // Store evaluation result for PDF download
      currentEvaluationResult = {
        type: 'apartment',
        data: evaluationData,
        result: result
      }
      
      // Show result
      showEvaluationResult(result, 'apartment')
    } else {
      throw new Error('Evaluation failed')
    }
    
  } catch (error) {
    console.error('Error evaluating apartment:', error)
    alert('Произошла ошибка при оценке. Попробуйте еще раз.')
  } finally {
    // Reset button
    submitBtn.disabled = false
    submitBtn.innerHTML = originalText
    lucide.createIcons()
  }
}

// Handle car evaluation
async function handleCarEvaluation(form) {
  const submitBtn = form.querySelector('button[type="submit"]')
  const originalText = submitBtn.innerHTML
  
  try {
    // Show loading
    submitBtn.disabled = true
    submitBtn.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-4 w-4 inline animate-spin"></i>Оценка...'
    lucide.createIcons()
    
    // Get form data
    const formData = new FormData(form)
    const data = Object.fromEntries(formData.entries())
    
    // Get selected features from checkboxes
    const featuresCheckboxes = Array.from(form.querySelectorAll('input[name="features"]:checked')).map(cb => cb.value)
    
    // Prepare evaluation data
    const evaluationData = {
      brand: data.brand,
      model: data.model,
      year: parseInt(data.year),
      engine_volume: parseFloat(data.engine_volume),
      fuel: data.fuel,
      transmission: data.transmission || "Mexanik",
      body_type: data.body_type,
      mileage: parseInt(data.mileage),
      color: data.color || "Oq",
      condition: data.condition || "Yaxshi",
      state: data.state,
      ownership: data.ownership || "Xususiy",
      owners_count: parseInt(data.owners_count) || 1,
      features: featuresCheckboxes,
      month: new Date().getMonth() + 1
    }
    
    // Call evaluation API
    const result = await evaluateCarAPI(evaluationData)
    
    if (result) {
      // Store evaluation result for PDF download
      currentEvaluationResult = {
        type: 'car',
        data: evaluationData,
        result: result
      }
      
      // Show result
      showEvaluationResult(result, 'car')
    } else {
      throw new Error('Evaluation failed')
    }
    
  } catch (error) {
    console.error('Error evaluating car:', error)
    alert('Произошла ошибка при оценке. Попробуйте еще раз.')
  } finally {
    // Reset button
    submitBtn.disabled = false
    submitBtn.innerHTML = originalText
    lucide.createIcons()
  }
}

// Show evaluation result
function showEvaluationResult(result, assetType) {
  const step2 = document.getElementById('evaluate-step-2')
  const resultDiv = document.getElementById('evaluate-result')
  
  step2.classList.add('hidden')
  resultDiv.classList.remove('hidden')
  
  const assetTypeText = assetType === 'apartment' ? 'квартиры' : 'автомобиля'
  const iconName = assetType === 'apartment' ? 'building-2' : 'car'
  const iconColor = assetType === 'apartment' ? 'text-blue-600' : 'text-green-600'
  
  // Handle price range format - API returns array [lower, upper] for apartments
  let priceRangeText = ''
  if (result.formatted_range) {
    priceRangeText = result.formatted_range
  } else if (Array.isArray(result.price_range)) {
    // For apartment API - returns [lower, upper]
    priceRangeText = `$${result.price_range[0].toLocaleString()} - $${result.price_range[1].toLocaleString()}`
  } else if (result.price_range && result.price_range.lower && result.price_range.upper) {
    // For car API - returns {lower, upper}
    priceRangeText = `$${result.price_range.lower.toLocaleString()} - $${result.price_range.upper.toLocaleString()}`
  }
  
  resultDiv.innerHTML = `
    <div class="text-center">
      <div class="mb-6">
        <i data-lucide="${iconName}" class="w-16 h-16 mx-auto mb-4 ${iconColor}"></i>
        <h3 class="text-2xl font-bold mb-4">Оценка ${assetTypeText}</h3>
      </div>
      
      <div class="bg-gray-50 dark:bg-gray-700 rounded-xl p-8 mb-6">
        <div class="text-sm text-gray-500 dark:text-gray-400 mb-2">Рыночная стоимость</div>
        <div class="text-4xl font-bold mb-4">${result.formatted_price || '$' + result.predicted_price.toLocaleString()}</div>
        <div class="text-sm text-gray-600 dark:text-gray-300">
          Диапазон: ${priceRangeText}
        </div>
        <div class="text-xs text-gray-400 mt-2">
          Точность модели: ±3.61%
        </div>
      </div>
      
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <button 
          onclick="downloadEvaluationReport()"
          class="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition flex items-center justify-center"
        >
          <i data-lucide="download" class="mr-2 h-5 w-5"></i>
          Скачать отчет
        </button>
        <button 
          onclick="document.getElementById('evaluate-step-1').classList.remove('hidden'); document.getElementById('evaluate-result').classList.add('hidden')"
          class="border border-gray-300 dark:border-gray-600 px-6 py-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition flex items-center justify-center"
        >
          <i data-lucide="refresh-cw" class="mr-2 h-5 w-5"></i>
          Оценить еще
        </button>
      </div>
    </div>
  `
  
  lucide.createIcons()
}

// Download evaluation report
async function downloadEvaluationReport() {
  if (!currentEvaluationResult) {
    alert('Нет данных для скачивания отчета')
    return
  }
  
  try {
    const endpoint = currentEvaluationResult.type === 'apartment' 
      ? '/download-apartment-report/'
      : '/download-car-report/'
    
    // Prepare price range string based on format
    let priceRangeStr = ''
    if (currentEvaluationResult.result.formatted_range) {
      priceRangeStr = currentEvaluationResult.result.formatted_range
    } else if (Array.isArray(currentEvaluationResult.result.price_range)) {
      // For apartment API - returns [lower, upper]
      priceRangeStr = `$${currentEvaluationResult.result.price_range[0].toLocaleString()} - $${currentEvaluationResult.result.price_range[1].toLocaleString()}`
    } else if (currentEvaluationResult.result.price_range && currentEvaluationResult.result.price_range.lower) {
      // For car API - returns {lower, upper}
      priceRangeStr = `$${currentEvaluationResult.result.price_range.lower.toLocaleString()} - $${currentEvaluationResult.result.price_range.upper.toLocaleString()}`
    }
    
    // Prepare data for PDF generation
    const pdfData = {
      ...currentEvaluationResult.data,
      predicted_price: currentEvaluationResult.result.predicted_price,
      price_range: priceRangeStr
    }
    
    const response = await apiCall(endpoint, {
      method: 'POST',
      body: JSON.stringify(pdfData)
    })
    
    if (response && response.ok) {
      // Create download link
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `${currentEvaluationResult.type}_evaluation_report.pdf`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } else {
      throw new Error('Failed to generate PDF')
    }
  } catch (error) {
    console.error('Error downloading report:', error)
    alert('Произошла ошибка при скачивании отчета')
  }
}

// Initialize evaluation when page loads
document.addEventListener('DOMContentLoaded', function() {
  // Add evaluation navigation
  addEvaluationNavigation()
  
  // Add evaluation button handlers
  initializeEvaluationButtons()
})

// Initialize evaluation buttons
function initializeEvaluationButtons() {
  // Wait for elements to be available
  setTimeout(() => {
    const evaluateButtons = document.querySelectorAll('.evaluate-asset-type-btn')
    evaluateButtons.forEach(button => {
      button.addEventListener('click', function() {
        const assetType = this.getAttribute('data-evaluate-type')
        renderEvaluationForm(assetType)
      })
    })
  }, 100)
}

// Add evaluation API endpoints
async function evaluateApartmentAPI(apartmentData) {
  try {
    const response = await apiCall('/evaluate/apartment/', {
      method: 'POST',
      body: JSON.stringify(apartmentData)
    });
    if (response && response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error('Error evaluating apartment:', error);
    return null;
  }
}

async function evaluateCarAPI(carData) {
  try {
    const response = await apiCall('/evaluate-car/', {
      method: 'POST',
      body: JSON.stringify(carData)
    });
    if (response && response.ok) {
      return await response.json();
    }
    return null;
  } catch (error) {
    console.error('Error evaluating car:', error);
    return null;
  }
}

// --- MARKET FUNCTIONS ---

// PowerBI URLs for the dashboards
const POWERBI_URLS = {
  apartments: 'https://app.powerbi.com/view?r=eyJrIjoiNWVhZmEwNjItYmE5NC00MjY1LTg2MGUtMGUyNmMxMmMzNWVlIiwidCI6ImI1OGVhYjJiLTA1YzYtNDcxYi1hYWRhLWNiNjMwY2MyMDJkYyIsImMiOjEwfQ%3D%3D',
  cars: 'https://app.powerbi.com/view?r=eyJrIjoiMWE0Y2Q4ZDItZWY2Yi00OTczLWFiMjgtYTkyYzQzZTNkYWMxIiwidCI6ImI1OGVhYjJiLTA1YzYtNDcxYi1hYWRhLWNiNjMwY2MyMDJkYyIsImMiOjEwfQ%3D%3D'
};

// Initialize market event handlers
function initializeMarketHandlers() {
  // Market type selection buttons
  const marketButtons = document.querySelectorAll('.market-type-btn');
  marketButtons.forEach(button => {
    button.addEventListener('click', () => {
      const marketType = button.getAttribute('data-market-type');
      showMarketDashboard(marketType);
    });
  });

  // Back to market selection button
  const backToSelection = document.getElementById('back-to-market-selection');
  if (backToSelection) {
    backToSelection.addEventListener('click', () => {
      showMarketSelection();
    });
  }
}

// Show market dashboard for specific type
function showMarketDashboard(marketType) {
  const marketSelection = document.getElementById('market-selection');
  const marketDashboard = document.getElementById('market-dashboard');
  const dashboardTitle = document.getElementById('market-dashboard-title');
  const powerbiIframe = document.getElementById('powerbi-iframe');

  // Hide selection, show dashboard
  if (marketSelection) marketSelection.classList.add('hidden');
  if (marketDashboard) marketDashboard.classList.remove('hidden');

  // Set title and iframe source
  if (marketType === 'apartments') {
    dashboardTitle.textContent = 'Аналитика рынка квартир';
    powerbiIframe.src = POWERBI_URLS.apartments;
  } else if (marketType === 'cars') {
    dashboardTitle.textContent = 'Аналитика рынка автомобилей';
    powerbiIframe.src = POWERBI_URLS.cars;
  }

  lucide.createIcons();
}

// Show market selection screen
function showMarketSelection() {
  const marketSelection = document.getElementById('market-selection');
  const marketDashboard = document.getElementById('market-dashboard');
  const powerbiIframe = document.getElementById('powerbi-iframe');

  // Show selection, hide dashboard
  if (marketSelection) marketSelection.classList.remove('hidden');
  if (marketDashboard) marketDashboard.classList.add('hidden');
  
  // Clear iframe to stop loading
  if (powerbiIframe) powerbiIframe.src = '';

  lucide.createIcons();
}

// Function to handle asset deletion with confirmation
async function handleDeleteAsset(asset) {
  // Show confirmation dialog
  const isConfirmed = confirm(`Вы действительно хотите удалить актив "${asset.name}"?\n\nЭто действие нельзя отменить.`);
  
  if (!isConfirmed) {
    return;
  }

  try {
    // Call API to delete asset
    const response = await apiCall(`/assets/${asset.id}/`, {
      method: 'DELETE'
    });

    if (response.ok) {
      // Remove asset from local array
      const assetIndex = assets.findIndex(a => a.id === asset.id);
      if (assetIndex !== -1) {
        assets.splice(assetIndex, 1);
      }

      // Reload dashboard data
      await loadAppData();

      // Navigate back to dashboard
      navigateTo('dashboard');

      // Show success message
      console.log('Asset deleted successfully');
    } else {
      throw new Error('Failed to delete asset');
    }
  } catch (error) {
    console.error('Error deleting asset:', error);
    alert('Ошибка при удалении актива. Попробуйте снова.');
  }
}

// Function to handle update evaluation
async function handleUpdateEvaluation(asset) {
  // Navigate to a special update evaluation view
  currentView = 'update-evaluation';
  selectedAssetId = asset.id;

  // Clear all sidebar navigation items
  document.querySelectorAll('.sidebar-link').forEach(link => {
    link.classList.remove('active');
  });

  // Hide all views
  dashboardView.classList.add('hidden');
  assetDetailView.classList.add('hidden');
  addAssetView.classList.add('hidden');
  
  const evaluateView = document.getElementById('evaluate-view');
  if (evaluateView) {
    evaluateView.classList.add('hidden');
  }

  const marketView = document.getElementById('market-view');
  if (marketView) {
    marketView.classList.add('hidden');
  }

  // Show update evaluation view
  showUpdateEvaluationView(asset);
}

// Function to show update evaluation view
function showUpdateEvaluationView(asset) {
  // Set page title
  pageTitle.textContent = `Обновить оценку: ${asset.name}`;
  backButton.classList.remove('hidden');

  // Create or update the update evaluation view
  let updateEvaluationView = document.getElementById('update-evaluation-view');
  if (!updateEvaluationView) {
    updateEvaluationView = document.createElement('div');
    updateEvaluationView.id = 'update-evaluation-view';
    updateEvaluationView.className = 'hidden animate-fade-in max-w-4xl mx-auto';
    viewContainer.appendChild(updateEvaluationView);
  }

  // Parse asset details
  let assetDetails = {};
  try {
    assetDetails = asset.description ? JSON.parse(asset.description) : {};
  } catch (e) {
    console.error('Error parsing asset details:', e);
  }

  updateEvaluationView.innerHTML = `
    <div class="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg">
      <div class="mb-6">
        <h3 class="text-2xl font-bold mb-2">Обновить оценку актива</h3>
        <p class="text-gray-600 dark:text-gray-400">Измените параметры актива и получите новую оценку стоимости</p>
      </div>
      
      <div id="update-evaluation-form-container">
        <!-- Form will be injected here -->
      </div>
    </div>
  `;

  updateEvaluationView.classList.remove('hidden');

  // Generate and populate the form based on asset type
  if (asset.asset_type === 'apartment') {
    renderUpdateApartmentForm(asset, assetDetails);
  } else if (asset.asset_type === 'car') {
    renderUpdateCarForm(asset, assetDetails);
  }
}

// Function to render apartment update form with pre-populated data
function renderUpdateApartmentForm(asset, assetDetails) {
  const formContainer = document.getElementById('update-evaluation-form-container');
  
  formContainer.innerHTML = generateApartmentEvaluationForm();
  
  // Pre-populate form with existing data - increased timeout to ensure form is fully rendered
  setTimeout(() => {
    const form = document.getElementById('apartment-evaluation-form'); // Fixed form ID
    if (form) {
      console.log('=== APARTMENT PRE-POPULATION DEBUG ===');
      console.log('Asset details for pre-population:', assetDetails);
      console.log('Full asset object:', asset);
      console.log('Asset description raw:', asset.description);
      console.log('Form element found:', form);
      console.log('All form inputs:', form.querySelectorAll('input, select'));
      
      // Parse and populate apartment specific fields
      if (assetDetails['Кол-во комнат']) {
        const roomsInput = form.querySelector('[name="rooms"]');
        console.log('Rooms input found:', roomsInput);
        if (roomsInput) {
          roomsInput.value = assetDetails['Кол-во комнат'];
          console.log('Set rooms to:', assetDetails['Кол-во комнат']);
        }
      }
      if (assetDetails['Площадь']) {
        const area = assetDetails['Площадь'].replace(' м²', '');
        const areaInput = form.querySelector('[name="area"]');
        console.log('Area input found:', areaInput);
        if (areaInput) {
          areaInput.value = area;
          console.log('Set area to:', area);
        }
      }
      if (assetDetails['Этаж']) {
        const floorInput = form.querySelector('[name="floor"]');
        console.log('Floor input found:', floorInput);
        if (floorInput) {
          floorInput.value = assetDetails['Этаж'];
          console.log('Set floor to:', assetDetails['Этаж']);
        }
      }
      if (assetDetails['Всего этажей']) {
        const totalFloorsInput = form.querySelector('[name="total_floors"]');
        console.log('Total floors input found:', totalFloorsInput);
        if (totalFloorsInput) {
          totalFloorsInput.value = assetDetails['Всего этажей'];
          console.log('Set total floors to:', assetDetails['Всего этажей']);
        }
      }
      
      // Populate select fields with proper value mapping
      const fieldMappings = {
        'Тип здания': { fieldName: 'bino_turi', valueMap: {
          'Новостройка': 'Yangi_qurilgan_uylar',
          'Вторичный рынок': 'Ikkilamchi_bozor',
          'Ikkinchi bozor': 'Ikkilamchi_bozor' // Legacy mapping
        }},
        'Тип строения': { fieldName: 'qurilish_turi', valueMap: {
          'Панельный': 'Panelli',
          'Монолитный': 'Monolitli', 
          'Кирпичный': 'G_ishtli',
          'Блочный': 'Blokli',
          'Деревянный': 'Yog_ochli',
          'Panel': 'Panelli', // Legacy mapping
          'Monolit': 'Monolitli',
          'G\'isht': 'G_ishtli',
          'Blok': 'Blokli',
          'Yog\'och': 'Yog_ochli'
        }}, 
        'Планировка': { fieldName: 'planirovka', valueMap: {
          'Раздельная': 'Alohida_ajratilgan',
          'Смешанная': 'Aralash',
          'Смешанная раздельная': 'Aralash_alohida',
          'Для малых семей': 'Kichik_oilalar_uchun',
          'Многоуровневая': 'Ko_p_darajali',
          'Пентхаус': 'Pentxaus',
          'Студия': 'Studiya'
        }},
        'Ремонт': { fieldName: 'renovation', valueMap: {
          'Хороший': 'Yaxshi',
          'Отличный': 'Zo_r',
          'Плохой': 'Qoniqarsiz'
        }},
        'Санузел': { fieldName: 'sanuzel', valueMap: {
          'Раздельный': 'Alohida',
          'Совмещенный': 'Aralash',
          '2 и более санузлов': '2_va_undan_ko_p_sanuzel'
        }},
        'Собственность': { fieldName: 'owner', valueMap: {
          'Частная': 'Xususiy',
          'Бизнес': 'Biznes'
        }},
        'Мебель': { fieldName: 'mebel', valueMap: {
          'Без мебели': 'Yo\'q',
          'С мебелью': 'Ha'
        }},
        'Можно договориться': { fieldName: 'kelishsa', valueMap: {
          'Да': 'Yes',
          'Нет': 'No'
        }}
      };

      Object.entries(fieldMappings).forEach(([detailKey, config]) => {
        if (assetDetails[detailKey]) {
          console.log(`Trying to populate ${config.fieldName} with value from ${detailKey}:`, assetDetails[detailKey]);
          const select = form.querySelector(`[name="${config.fieldName}"]`);
          if (select) {
            let valueToSet = assetDetails[detailKey];
            
            // Check if we need to map the stored value to form value
            if (config.valueMap && config.valueMap[valueToSet]) {
              valueToSet = config.valueMap[valueToSet];
              console.log(`Mapped "${assetDetails[detailKey]}" to "${valueToSet}"`);
            } else if (config.valueMap) {
              // Try to find by checking if stored value matches any form value
              const foundFormValue = Object.values(config.valueMap).find(formVal => formVal === valueToSet);
              if (foundFormValue) {
                valueToSet = foundFormValue;
                console.log(`Using stored value directly: "${valueToSet}"`);
              } else {
                console.log(`No mapping found for "${valueToSet}" in field ${config.fieldName}`);
              }
            }
            
            select.value = valueToSet;
            console.log(`Set ${config.fieldName} to:`, valueToSet);
          } else {
            console.log(`Could not find select element for field: ${config.fieldName}`);
          }
        } else {
          console.log(`No value found for detail key: ${detailKey}`);
        }
      });

      // Handle district and mahalla
      if (assetDetails['Район']) {
        const districtSelect = form.querySelector('[name="district"]');
        console.log('District select found:', districtSelect);
        if (districtSelect) {
          districtSelect.value = assetDetails['Район'];
          console.log('Set district to:', assetDetails['Район']);
          // Trigger change event to load mahallas
          districtSelect.dispatchEvent(new Event('change'));
          
          // Set mahalla after a delay to allow mahallas to load
          setTimeout(() => {
            if (assetDetails['Махалля']) {
              const mahallaSelect = form.querySelector('[name="mahalla"]');
              console.log('Mahalla select found:', mahallaSelect);
              if (mahallaSelect) {
                mahallaSelect.value = assetDetails['Махалля'];
                console.log('Set mahalla to:', assetDetails['Махалля']);
              }
            }
          }, 300);
        }
      }

      // Handle checkboxes for apartment features
      if (assetDetails['В доме'] && assetDetails['В доме'] !== 'Не указано') {
        const uydaFeatures = assetDetails['В доме'].split(', ');
        console.log('Uyda features to check:', uydaFeatures);
        uydaFeatures.forEach(feature => {
          const checkbox = form.querySelector(`[name="uyda"][value="${feature}"]`);
          console.log(`Looking for uyda checkbox with value "${feature}":`, checkbox);
          if (checkbox) {
            checkbox.checked = true;
            console.log(`Checked uyda feature: ${feature}`);
          }
        });
      }
      
      if (assetDetails['Рядом с домом'] && assetDetails['Рядом с домом'] !== 'Не указано') {
        const atrofdaFeatures = assetDetails['Рядом с домом'].split(', ');
        console.log('Atrofda features to check:', atrofdaFeatures);
        atrofdaFeatures.forEach(feature => {
          const checkbox = form.querySelector(`[name="atrofda"][value="${feature}"]`);
          console.log(`Looking for atrofda checkbox with value "${feature}":`, checkbox);
          if (checkbox) {
            checkbox.checked = true;
            console.log(`Checked atrofda feature: ${feature}`);
          }
        });
      }

      // Initialize handlers for this form
      initializeApartmentEvaluationHandlers();
      
      // Replace the evaluate button with update button
      const evaluateBtn = form.querySelector('button[type="submit"]');
      if (evaluateBtn) {
        evaluateBtn.textContent = 'Обновить оценку';
        evaluateBtn.innerHTML = '<i data-lucide="refresh-cw" class="mr-2 h-4 w-4 inline"></i>Обновить оценку';
        lucide.createIcons();
        
        // Add event listener for update
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          await handleApartmentEvaluationUpdate(form, asset);
        });
      }
    } else {
      console.log('ERROR: evaluate-apartment-form not found!');
    }
  }, 500);
}

// Function to render car update form with pre-populated data
function renderUpdateCarForm(asset, assetDetails) {
  const formContainer = document.getElementById('update-evaluation-form-container');
  
  formContainer.innerHTML = generateCarEvaluationForm();
  
  // Pre-populate form with existing data
  setTimeout(async () => {
    // Load car brands first
    await loadCarBrandsForEvaluation();
    
    const form = document.getElementById('car-evaluation-form'); // Fixed form ID
    if (form) {
      console.log('=== CAR PRE-POPULATION DEBUG ===');
      console.log('Car asset details for pre-population:', assetDetails);
      console.log('Full car asset object:', asset);
      console.log('Car asset description raw:', asset.description);
      console.log('Car form element found:', form);
      console.log('All car form inputs:', form.querySelectorAll('input, select'));
      
      // Pre-populate basic fields
      if (assetDetails['Год выпуска']) {
        const yearInput = form.querySelector('[name="year"]');
        console.log('Year input found:', yearInput);
        if (yearInput) {
          yearInput.value = assetDetails['Год выпуска'];
          console.log('Set year to:', assetDetails['Год выпуска']);
        }
      }
      if (assetDetails['Пробег']) {
        const mileage = assetDetails['Пробег'].replace(' км', '').replace(/[^\d]/g, '');
        const mileageInput = form.querySelector('[name="mileage"]');
        console.log('Mileage input found:', mileageInput);
        if (mileageInput) {
          mileageInput.value = mileage;
          console.log('Set mileage to:', mileage);
        }
      }
      if (assetDetails['Объем двигателя']) {
        const engineVolume = assetDetails['Объем двигателя'].replace(' л', '');
        const engineInput = form.querySelector('[name="engine_volume"]');
        console.log('Engine input found:', engineInput);
        if (engineInput) {
          engineInput.value = engineVolume;
          console.log('Set engine volume to:', engineVolume);
        }
      }

      // Populate selects with proper value mapping
      const fieldMappings = {
        'Марка': { fieldName: 'brand', valueMap: null }, // No mapping needed, brand names should be exact
        'Топливо': { fieldName: 'fuel', valueMap: {
          'Бензин': 'Benzin',
          'Газ/Бензин': 'Gaz/Benzin',
          'Дизель': 'Dizel',
          'Гибрид': 'Gibrid',
          'Электро': 'Elektro',
          'Другое': 'Boshqa'
        }},
        'Тип кузова': { fieldName: 'body_type', valueMap: {
          'Седан': 'Sedan',
          'Хэтчбек': 'Xetchbek',
          'Универсал': 'Universal',
          'Внедорожник': 'Yo\'ltanlamas',
          'Купе': 'Kupe',
          'Минивэн': 'Miniven',
          'Пикап': 'Pikap',
          'Кабриолет': 'Kabriolet',
          'Другое': 'Boshqa'
        }},
        'Цвет': { fieldName: 'color', valueMap: {
          'Белый': 'Oq',
          'Черный': 'Qora',
          'Серебристый': 'Kumush',
          'Серый': 'Kulrang',
          'Синий': 'Ko\'k',
          'Коричневый': 'Jigarrang',
          'Бежевый': 'Bejeviy',
          'Асфальт': 'Asfalt',
          'Другой': 'Boshqa'
        }},
        'Состояние': { fieldName: 'condition', valueMap: {
          'Отличное': 'A\'lo',
          'Хорошее': 'Yaxshi',
          'Среднее': 'O\'rtacha',
          'Требует ремонта': 'Remont talab'
        }},
        'Коробка передач': { fieldName: 'transmission', valueMap: {
          'Механическая': 'Mexanik',
          'Автоматическая': 'Avtomat'
        }},
        'Тип собственности': { fieldName: 'ownership', valueMap: {
          'Частная': 'Xususiy',
          'Бизнес': 'Biznes'
        }},
        'Владельцев': { fieldName: 'owners_count', valueMap: null } // Direct mapping
      };

      Object.entries(fieldMappings).forEach(([detailKey, config]) => {
        if (assetDetails[detailKey]) {
          console.log(`Trying to populate car ${config.fieldName} with value from ${detailKey}:`, assetDetails[detailKey]);
          const select = form.querySelector(`[name="${config.fieldName}"]`);
          if (select) {
            let valueToSet = assetDetails[detailKey];
            
            // Check if we need to map the stored value to form value
            if (config.valueMap && config.valueMap[valueToSet]) {
              valueToSet = config.valueMap[valueToSet];
              console.log(`Mapped "${assetDetails[detailKey]}" to "${valueToSet}"`);
            } else if (config.valueMap) {
              // Try to find by checking if stored value matches any form value
              const foundFormValue = Object.values(config.valueMap).find(formVal => formVal === valueToSet);
              if (foundFormValue) {
                valueToSet = foundFormValue;
                console.log(`Using stored value directly: "${valueToSet}"`);
              } else {
                console.log(`No mapping found for "${valueToSet}" in field ${config.fieldName}`);
              }
            }
            
            select.value = valueToSet;
            console.log(`Set car ${config.fieldName} to:`, valueToSet);
          } else {
            console.log(`Could not find car select element for field: ${config.fieldName}`);
          }
        } else {
          console.log(`No value found for car detail key: ${detailKey}`);
        }
      });

      // Load models after brand is set
      if (assetDetails['Марка']) {
        console.log('Loading models for brand:', assetDetails['Марка']);
        await loadCarModelsForEvaluation(assetDetails['Марка']);
        if (assetDetails['Модель']) {
          const modelSelect = form.querySelector('[name="model"]');
          console.log('Model select found:', modelSelect);
          if (modelSelect) {
            modelSelect.value = assetDetails['Модель'];
            console.log('Set model to:', assetDetails['Модель']);
          }
        }
      }

      // Handle features checkboxes
      if (assetDetails['Опции'] && assetDetails['Опции'] !== 'Не указаны') {
        const features = assetDetails['Опции'].split(', ');
        console.log('Car features to check:', features);
        features.forEach(feature => {
          const checkbox = form.querySelector(`[name="features"][value="${feature}"]`);
          console.log(`Looking for car feature checkbox with value "${feature}":`, checkbox);
          if (checkbox) {
            checkbox.checked = true;
            console.log(`Checked car feature: ${feature}`);
          }
        });
      }

      // Initialize handlers for this form
      initializeCarEvaluationHandlers();
      
      // Replace the evaluate button with update button
      const evaluateBtn = form.querySelector('button[type="submit"]');
      if (evaluateBtn) {
        evaluateBtn.textContent = 'Обновить оценку';
        evaluateBtn.innerHTML = '<i data-lucide="refresh-cw" class="mr-2 h-4 w-4 inline"></i>Обновить оценку';
        lucide.createIcons();
        
        // Add event listener for update
        form.addEventListener('submit', async (e) => {
          e.preventDefault();
          await handleCarEvaluationUpdate(form, asset);
        });
      }
    } else {
      console.log('ERROR: evaluate-car-form not found!');
    }
  }, 500);
}

// Function to handle apartment evaluation update
async function handleApartmentEvaluationUpdate(form, asset) {
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-4 w-4 inline animate-spin"></i>Обновляем...';
  lucide.createIcons();

  try {
    // Get form data and evaluate
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Get checkboxes
    const uyda = Array.from(form.querySelectorAll('input[name="uyda"]:checked')).map(cb => cb.value);
    const atrofda = Array.from(form.querySelectorAll('input[name="atrofda"]:checked')).map(cb => cb.value);
    
    data.uyda = uyda;
    data.atrofda = atrofda;
    data.month = new Date().getMonth() + 1;
    data.year = new Date().getFullYear();

    // Evaluate apartment
    const evaluationResult = await evaluateApartmentAPI(data);
    
    if (evaluationResult && evaluationResult.predicted_price) {
      // Update asset with new evaluation
      const updateData = {
        current_value: evaluationResult.predicted_price,
        // Update the details with new form data
        details: JSON.stringify({
          'Кол-во комнат': data.rooms,
          'Площадь': `${data.area} м²`,
          'Этаж': data.floor,
          'Всего этажей': data.total_floors,
          'Тип здания': getDisplayValue('bino_turi', data.bino_turi),
          'Тип строения': getDisplayValue('qurilish_turi', data.qurilish_turi),
          'Планировка': getDisplayValue('planirovka', data.planirovka),
          'Ремонт': getDisplayValue('renovation', data.renovation),
          'Санузел': getDisplayValue('sanuzel', data.sanuzel),
          'Собственность': getDisplayValue('owner', data.owner),
          'Мебель': getDisplayValue('mebel', data.mebel),
          'Можно договориться': getDisplayValue('kelishsa', data.kelishsa),
          'В доме': uyda.join(', ') || 'Не указано',
          'Рядом с домом': atrofda.join(', ') || 'Не указано'
        })
      };

      const response = await apiCall(`/assets/${asset.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
      });

      if (response.ok) {
        const updatedAsset = await response.json();
        
        // Update local asset data
        const assetIndex = assets.findIndex(a => a.id === asset.id);
        if (assetIndex !== -1) {
          assets[assetIndex] = updatedAsset;
        }

        // Reload dashboard data
        await loadAppData();

        // Navigate back to asset detail
        navigateTo('asset-detail', asset.id);

        // Show success message
        alert(`Оценка успешно обновлена! Новая стоимость: $${evaluationResult.predicted_price.toLocaleString()}`);
      } else {
        throw new Error('Failed to update asset');
      }
    } else {
      throw new Error('Evaluation failed');
    }
  } catch (error) {
    console.error('Error updating apartment evaluation:', error);
    alert('Ошибка при обновлении оценки. Попробуйте снова.');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
    lucide.createIcons();
  }
}

// Function to handle car evaluation update
async function handleCarEvaluationUpdate(form, asset) {
  const submitBtn = form.querySelector('button[type="submit"]');
  const originalText = submitBtn.innerHTML;
  submitBtn.disabled = true;
  submitBtn.innerHTML = '<i data-lucide="loader-2" class="mr-2 h-4 w-4 inline animate-spin"></i>Обновляем...';
  lucide.createIcons();

  try {
    // Get form data and evaluate
    const formData = new FormData(form);
    const data = Object.fromEntries(formData.entries());
    
    // Get features checkboxes
    const features = Array.from(form.querySelectorAll('input[name="features"]:checked')).map(cb => cb.value);
    data.features = features;

    // Evaluate car
    const evaluationResult = await evaluateCarAPI(data);
    
    if (evaluationResult && evaluationResult.predicted_price) {
      // Update asset with new evaluation
      const updateData = {
        current_value: evaluationResult.predicted_price,
        // Update the details with new form data
        details: JSON.stringify({
          'Марка': data.brand,
          'Модель': data.model,
          'Год выпуска': data.year,
          'Объем двигателя': `${data.engine_volume} л`,
          'Топливо': data.fuel,
          'Тип собственности': data.ownership || 'Частная',
          'Тип кузова': data.body_type,
          'Цвет': data.color,
          'Состояние': data.condition,
          'Владельцев': data.owners_count || '1',
          'Пробег': `${data.mileage} км`,
          'Коробка передач': data.transmission || 'Механическая',
          'Опции': features.length > 0 ? features.join(', ') : 'Не указаны'
        })
      };

      const response = await apiCall(`/assets/${asset.id}/`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updateData)
      });

      if (response.ok) {
        const updatedAsset = await response.json();
        
        // Update local asset data
        const assetIndex = assets.findIndex(a => a.id === asset.id);
        if (assetIndex !== -1) {
          assets[assetIndex] = updatedAsset;
        }

        // Reload dashboard data
        await loadAppData();

        // Navigate back to asset detail
        navigateTo('asset-detail', asset.id);

        // Show success message
        alert(`Оценка успешно обновлена! Новая стоимость: $${evaluationResult.predicted_price.toLocaleString()}`);
      } else {
        throw new Error('Failed to update asset');
      }
    } else {
      throw new Error('Evaluation failed');
    }
  } catch (error) {
    console.error('Error updating car evaluation:', error);
    alert('Ошибка при обновлении оценки. Попробуйте снова.');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerHTML = originalText;
    lucide.createIcons();
  }
}

// Helper function to get display values for form fields
function getDisplayValue(fieldType, value) {
  // This function maps internal field values to display values
  const mappings = {
    'bino_turi': {
      'Yangi_qurilgan_uylar': 'Новостройка',
      'Ikkilamchi_bozor': 'Вторичный рынок',
      'Ikkinchi bozor': 'Вторичный рынок'
    },
    'qurilish_turi': {
      'Panelli': 'Панельный',
      'Monolitli': 'Монолитный',
      'G_ishtli': 'Кирпичный',
      'Panel': 'Панельный',
      'Monolit': 'Монолитный',
      'G\'isht': 'Кирпичный'
    },
    'planirovka': {
      'Alohida_ajratilgan': 'Раздельная',
      'Aralash': 'Смешанная',
      'Oddiy': 'Обычная'
    },
    'renovation': {
      'Yaxshi': 'Хороший',
      'Zo_r': 'Отличный',
      'Qoniqarsiz': 'Плохой',
      'O\'rta': 'Средний'
    },
    'sanuzel': {
      'Alohida': 'Раздельный',
      'Aralash': 'Совмещенный',
      'Birgalikda': 'Совмещенный'
    },
    'owner': {
      'Xususiy': 'Частная',
      'Biznes': 'Бизнес',
      'Mulkdor': 'Собственник'
    },
    'mebel': {
      'Yo\'q': 'Без мебели',
      'Ha': 'С мебелью'
    },
    'kelishsa': {
      'Yes': 'Да',
      'No': 'Нет',
      'Ha': 'Да',
      'Yo\'q': 'Нет'
    }
  };

  if (mappings[fieldType] && mappings[fieldType][value]) {
    return mappings[fieldType][value];
  }
  return value;
}

// ========== MARKETPLACE FUNCTIONALITY ==========

// Handle putting asset in sales
async function handlePutInSales(asset) {
  try {
    console.log('handlePutInSales called with asset:', asset);
    console.log('Auth token:', getAuthToken());
    console.log('Is authenticated:', isAuthenticated());
    
    // Check authentication first
    if (!isAuthenticated()) {
      alert('Необходимо войти в систему для выставления активов на продажу');
      return;
    }
    
    // Show confirmation dialog
    const confirmed = confirm(`Вы уверены, что хотите выставить "${asset.name}" на продажу?`);
    if (!confirmed) return;

    console.log('Creating marketplace listing for asset:', asset.id);

    // Create marketplace listing
    const response = await apiCall('/marketplace/create/', {
      method: 'POST',
      body: JSON.stringify({
        asset_id: asset.id,
        listing_price: asset.current_value,
        description: `${asset.name} - ${asset.address}`
      })
    });

    console.log('Marketplace create response:', response);

    if (response.ok) {
      const result = await response.json();
      console.log('Marketplace listing created:', result);
      alert('Актив успешно выставлен на продажу! Теперь он доступен в разделе "Объявления".');
      
      // Reload dashboard data to reflect changes
      await loadAppData();
      
      // Navigate to announcements to show the listing
      navigateTo('announcements');
    } else if (response.status === 401) {
      console.error('Authentication failed - logging out');
      alert('Сессия истекла. Пожалуйста, войдите в систему заново.');
      logout();
    } else {
      // Try to parse error response
      let errorMessage = 'Ошибка при выставлении актива на продажу';
      try {
        const error = await response.json();
        errorMessage = error.error || error.message || errorMessage;
      } catch (e) {
        const errorText = await response.text();
        console.error('Error response text:', errorText);
      }
      console.error('Marketplace create error:', response.status, errorMessage);
      alert(errorMessage);
    }
  } catch (error) {
    console.error('Error putting asset in sales:', error);
    alert('Ошибка при выставлении актива на продажу');
  }
}

// Load marketplace listings
async function loadMarketplaceListings(filters = {}) {
  try {
    console.log('loadMarketplaceListings called with filters:', filters);
    console.log('Auth token:', getAuthToken());
    console.log('Is authenticated:', isAuthenticated());
    
    const queryParams = new URLSearchParams();
    
    if (filters.asset_type) queryParams.append('asset_type', filters.asset_type);
    if (filters.min_price) queryParams.append('min_price', filters.min_price);
    if (filters.max_price) queryParams.append('max_price', filters.max_price);
    
    const url = `/marketplace/listings/${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    console.log('Making request to:', url);
    
    const response = await apiCall(url);
    console.log('Marketplace listings response:', response);
    
    if (response.ok) {
      const listings = await response.json();
      console.log('Marketplace listings data:', listings);
      renderMarketplaceListings(listings);
      return listings;
    } else {
      const errorText = await response.text();
      console.error('Marketplace listings error response:', response.status, errorText);
      throw new Error(`Failed to load marketplace listings: ${response.status} ${errorText}`);
    }
  } catch (error) {
    console.error('Error loading marketplace listings:', error);
    showMarketplaceError('Ошибка при загрузке объявлений');
    return [];
  }
}

// Render marketplace listings
function renderMarketplaceListings(listings) {
  const grid = document.getElementById('announcements-grid');
  const emptyState = document.getElementById('announcements-empty');
  
  if (!grid) return;
  
  if (listings.length === 0) {
    grid.innerHTML = '';
    if (emptyState) emptyState.classList.remove('hidden');
    return;
  }
  
  if (emptyState) emptyState.classList.add('hidden');
  
  grid.innerHTML = listings.map(listing => {
    const asset = listing.asset;
    const assetIcon = asset.asset_type === 'apartment' ? 'building-2' : 'car';
    const assetColor = asset.asset_type === 'apartment' ? 'blue' : 'green';
    
    // Get key details for display
    let keyDetails = '';
    if (asset.details) {
      if (asset.asset_type === 'apartment') {
        const rooms = asset.details['Кол-во комнат'] || '';
        const area = asset.details['Площадь'] || '';
        const floor = asset.details['Этаж'] || '';
        keyDetails = `${rooms ? rooms + '-комн.' : ''} ${area ? area : ''} ${floor ? floor + ' этаж' : ''}`.trim();
      } else if (asset.asset_type === 'car') {
        const brand = asset.details['Марка'] || '';
        const model = asset.details['Модель'] || '';
        const year = asset.details['Год выпуска'] || '';
        keyDetails = `${brand} ${model} ${year}`.trim();
      }
    }
    
    return `
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
        <div class="p-6">
          <!-- Header -->
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center">
              <div class="w-12 h-12 rounded-full bg-${assetColor}-100 dark:bg-${assetColor}-900/50 flex items-center justify-center mr-3">
                <i data-lucide="${assetIcon}" class="w-6 h-6 text-${assetColor}-600 dark:text-${assetColor}-400"></i>
              </div>
              <div>
                <h3 class="text-lg font-semibold">${asset.name}</h3>
                <p class="text-sm text-gray-500 dark:text-gray-400">${keyDetails}</p>
              </div>
            </div>
            <div class="text-right">
              <div class="text-2xl font-bold text-green-600">${listing.formatted_price}</div>
            </div>
          </div>
          
          <!-- Details -->
          <div class="space-y-2 mb-4">
            <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <i data-lucide="map-pin" class="w-4 h-4 mr-2"></i>
              ${asset.address}
            </div>
            <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <i data-lucide="user" class="w-4 h-4 mr-2"></i>
              ${listing.seller.username}
            </div>
            <div class="flex items-center text-sm text-gray-600 dark:text-gray-400">
              <i data-lucide="calendar" class="w-4 h-4 mr-2"></i>
              ${new Date(listing.listed_at).toLocaleDateString('ru-RU')}
            </div>
          </div>
          
          <!-- Description -->
          ${listing.description ? `
            <div class="mb-4">
              <p class="text-sm text-gray-700 dark:text-gray-300">${listing.description}</p>
            </div>
          ` : ''}
          
          <!-- Contact buttons -->
          <div class="flex gap-2">
            ${listing.seller.phone ? `
              <a href="tel:${listing.seller.phone}" class="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition text-center text-sm">
                <i data-lucide="phone" class="w-4 h-4 inline mr-1"></i>
                Позвонить
              </a>
            ` : ''}
            <a href="mailto:${listing.seller.email}" class="flex-1 bg-gray-600 text-white px-4 py-2 rounded-lg hover:bg-gray-700 transition text-center text-sm">
              <i data-lucide="mail" class="w-4 h-4 inline mr-1"></i>
              Написать
            </a>
          </div>
          
          ${listing.is_own_listing ? `
            <div class="mt-2">
              <button onclick="removeMarketplaceListing(${listing.id})" class="w-full bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition text-sm">
                <i data-lucide="x" class="w-4 h-4 inline mr-1"></i>
                Снять с продажи
              </button>
            </div>
          ` : ''}
        </div>
      </div>
    `;
  }).join('');
  
  // Reinitialize Lucide icons
  lucide.createIcons();
}

// Show marketplace error
function showMarketplaceError(message) {
  const grid = document.getElementById('announcements-grid');
  const emptyState = document.getElementById('announcements-empty');
  
  if (grid) {
    grid.innerHTML = `
      <div class="col-span-full text-center py-12">
        <i data-lucide="alert-circle" class="w-16 h-16 mx-auto mb-4 text-red-400"></i>
        <h3 class="text-xl font-semibold mb-2 text-red-600">${message}</h3>
        <button onclick="loadMarketplaceListings()" class="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition">
          Попробовать снова
        </button>
      </div>
    `;
    lucide.createIcons();
  }
  
  if (emptyState) emptyState.classList.add('hidden');
}

// Remove marketplace listing
async function removeMarketplaceListing(listingId) {
  try {
    const confirmed = confirm('Вы уверены, что хотите снять объявление с продажи?');
    if (!confirmed) return;

    const response = await apiCall(`/marketplace/listings/${listingId}/`, {
      method: 'DELETE'
    });

    if (response.ok) {
      alert('Объявление успешно снято с продажи');
      
      // Reload listings
      const currentFilters = getCurrentMarketplaceFilters();
      await loadMarketplaceListings(currentFilters);
    } else {
      const error = await response.json();
      alert(error.error || 'Ошибка при снятии объявления');
    }
  } catch (error) {
    console.error('Error removing marketplace listing:', error);
    alert('Ошибка при снятии объявления');
  }
}

// Get current marketplace filters
function getCurrentMarketplaceFilters() {
  const typeFilter = document.getElementById('announcement-filter-type');
  const minPriceFilter = document.getElementById('announcement-filter-price-min');
  const maxPriceFilter = document.getElementById('announcement-filter-price-max');
  
  return {
    asset_type: typeFilter ? typeFilter.value : '',
    min_price: minPriceFilter ? minPriceFilter.value : '',
    max_price: maxPriceFilter ? maxPriceFilter.value : ''
  };
}

// Initialize marketplace functionality
function initializeMarketplace() {
  console.log('Initializing marketplace...');
  console.log('Auth token:', getAuthToken());
  console.log('Is authenticated:', isAuthenticated());
  
  // Check if user is authenticated before loading listings
  if (!isAuthenticated()) {
    console.error('User not authenticated, redirecting to login');
    showMarketplaceError('Необходимо войти в систему для просмотра объявлений');
    return;
  }
  
  // Load initial listings
  loadMarketplaceListings();
  
  // Set up filter handlers
  const applyFiltersBtn = document.getElementById('apply-announcement-filters');
  if (applyFiltersBtn) {
    applyFiltersBtn.addEventListener('click', () => {
      const filters = getCurrentMarketplaceFilters();
      loadMarketplaceListings(filters);
    });
  }
  
  // Set up Enter key handler for price filters
  const priceInputs = document.querySelectorAll('#announcement-filter-price-min, #announcement-filter-price-max');
  priceInputs.forEach(input => {
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        const filters = getCurrentMarketplaceFilters();
        loadMarketplaceListings(filters);
      }
    });
  });
}


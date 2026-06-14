// Tanzania Locations JavaScript
// Hii script inawajibika kupakia Mikoa, Wilaya, na Kata za Tanzania

// Global variable kuhifadhi data
let tanzaniaData = null;
let currentRegion = null;
let currentDistrict = null;

// Function to load data from JSON file
async function loadTanzaniaLocations() {
    try {
        // RECOMMENDED: Tumia url_for style au absolute path
        const response = await fetch('/static/data/tanzania_locations.json');

        // KAMA HAPO JUU HAIJAFANYA KAZI, jaribu hii:
        // const response = await fetch('/app/static/data/tanzania_locations.json');
        // AU
        // const response = await fetch('/static/data/tanzania_locations.json?_=' + Date.now());

        if (!response.ok) {
            throw new Error('HTTP error! status: ' + response.status);
        }
        tanzaniaData = await response.json();
        console.log('✅ Data ya Tanzania imepakiwa:', tanzaniaData);
        console.log('📊 Mikoa iliyopatikana: ' + tanzaniaData.regions.length);
        populateRegions();
    } catch (error) {
        console.error('❌ Error loading Tanzania locations:', error);
        showErrorAlert('Imeshindwa kupakia data za mikoa. Tafadhali onyesha upya ukurasa.');
    }
}

// Fallback data ikiwa JSON haipatikani
function loadFallbackData() {
    tanzaniaData = {
        regions: [
            { name: "Arusha", districts: [{ name: "Arusha City", wards: ["Sokon I", "Sokon II", "Kati"] }] },
            { name: "Dar es Salaam", districts: [{ name: "Ilala", wards: ["Kivukoni", "Kariakoo", "Gerezani"] }] },
            { name: "Mwanza", districts: [{ name: "Nyamagana", wards: ["Mkolani", "Igogo", "Pamba"] }] },
            { name: "Dodoma", districts: [{ name: "Dodoma City", wards: ["Makole", "Kisasa", "Mlimani"] }] },
            { name: "Kilimanjaro", districts: [{ name: "Moshi City", wards: ["Mji Mpya", "Kaloleni", "Kati"] }] }
        ]
    };
    populateRegions();
}

// Kujaza dropdown ya Mikoa
function populateRegions() {
    const regionSelect = document.getElementById('region');
    if (!regionSelect || !tanzaniaData) return;

    // Clear existing options (keep first option)
    while (regionSelect.options.length > 1) {
        regionSelect.remove(1);
    }

    // Add all regions
    tanzaniaData.regions.forEach(region => {
        const option = document.createElement('option');
        option.value = region.name;
        option.textContent = region.name;
        regionSelect.appendChild(option);
    });
}

// Kujaza Wilaya kulingana na Mkoa uliochaguliwa
function populateDistricts(regionName) {
    const districtSelect = document.getElementById('district');
    const wardSelect = document.getElementById('ward');

    if (!districtSelect) return;

    // Clear districts
    while (districtSelect.options.length > 1) {
        districtSelect.remove(1);
    }

    // Clear wards
    if (wardSelect) {
        while (wardSelect.options.length > 1) {
            wardSelect.remove(1);
        }
        wardSelect.disabled = true;
        wardSelect.options[0].textContent = '-- Kwanza chagua Wilaya --';
    }

    // Find region
    const region = tanzaniaData.regions.find(r => r.name === regionName);
    if (!region || !region.districts) {
        districtSelect.disabled = true;
        return;
    }

    // Add districts
    region.districts.forEach(district => {
        const option = document.createElement('option');
        option.value = district.name;
        option.textContent = district.name;
        districtSelect.appendChild(option);
    });

    districtSelect.disabled = false;
    currentRegion = regionName;
}

// Kujaza Kata kulingana na Wilaya iliyochaguliwa
function populateWards(districtName) {
    const wardSelect = document.getElementById('ward');
    if (!wardSelect || !currentRegion) return;

    // Clear wards
    while (wardSelect.options.length > 1) {
        wardSelect.remove(1);
    }

    // Find region and district
    const region = tanzaniaData.regions.find(r => r.name === currentRegion);
    if (!region) return;

    const district = region.districts.find(d => d.name === districtName);
    if (!district || !district.wards) {
        wardSelect.disabled = true;
        return;
    }

    // Add wards
    district.wards.forEach(ward => {
        const option = document.createElement('option');
        option.value = ward;
        option.textContent = ward;
        wardSelect.appendChild(option);
    });

    wardSelect.disabled = false;
    currentDistrict = districtName;
}

// Event listeners
document.addEventListener('DOMContentLoaded', function () {
    // Load Tanzania locations
    loadTanzaniaLocations();

    // Add event listener for region change
    const regionSelect = document.getElementById('region');
    if (regionSelect) {
        regionSelect.addEventListener('change', function () {
            if (this.value) {
                populateDistricts(this.value);
            } else {
                // Disable district and ward if no region selected
                const districtSelect = document.getElementById('district');
                const wardSelect = document.getElementById('ward');
                if (districtSelect) {
                    districtSelect.disabled = true;
                    while (districtSelect.options.length > 1) {
                        districtSelect.remove(1);
                    }
                }
                if (wardSelect) {
                    wardSelect.disabled = true;
                    while (wardSelect.options.length > 1) {
                        wardSelect.remove(1);
                    }
                }
            }
        });
    }

    // Add event listener for district change
    const districtSelect = document.getElementById('district');
    if (districtSelect) {
        districtSelect.addEventListener('change', function () {
            if (this.value) {
                populateWards(this.value);
            }
        });
    }
});
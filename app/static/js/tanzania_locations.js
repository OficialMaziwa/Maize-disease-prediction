
let tanzaniaData = null;
let currentRegion = null;
let currentDistrict = null;

async function loadTanzaniaLocations() {
    try {
        const response = await fetch('/static/data/tanzania_locations.json');
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

function populateRegions() {
    const regionSelect = document.getElementById('region');
    if (!regionSelect || !tanzaniaData) return;

    while (regionSelect.options.length > 1) {
        regionSelect.remove(1);
    }

    tanzaniaData.regions.forEach(region => {
        const option = document.createElement('option');
        option.value = region.name;
        option.textContent = region.name;
        regionSelect.appendChild(option);
    });
}

function populateDistricts(regionName) {
    const districtSelect = document.getElementById('district');
    const wardSelect = document.getElementById('ward');

    if (!districtSelect) return;

    while (districtSelect.options.length > 1) {
        districtSelect.remove(1);
    }

    if (wardSelect) {
        while (wardSelect.options.length > 1) {
            wardSelect.remove(1);
        }
        wardSelect.disabled = true;
        wardSelect.options[0].textContent = '-- Kwanza chagua Wilaya --';
    }

    const region = tanzaniaData.regions.find(r => r.name === regionName);
    if (!region || !region.districts) {
        districtSelect.disabled = true;
        return;
    }

    region.districts.forEach(district => {
        const option = document.createElement('option');
        option.value = district.name;
        option.textContent = district.name;
        districtSelect.appendChild(option);
    });

    districtSelect.disabled = false;
    currentRegion = regionName;
}

function populateWards(districtName) {
    const wardSelect = document.getElementById('ward');
    if (!wardSelect || !currentRegion) return;

    while (wardSelect.options.length > 1) {
        wardSelect.remove(1);
    }

    const region = tanzaniaData.regions.find(r => r.name === currentRegion);
    if (!region) return;

    const district = region.districts.find(d => d.name === districtName);
    if (!district || !district.wards) {
        wardSelect.disabled = true;
        return;
    }

    district.wards.forEach(ward => {
        const option = document.createElement('option');
        option.value = ward;
        option.textContent = ward;
        wardSelect.appendChild(option);
    });

    wardSelect.disabled = false;
    currentDistrict = districtName;
}

document.addEventListener('DOMContentLoaded', function () {
    loadTanzaniaLocations();

    const regionSelect = document.getElementById('region');
    if (regionSelect) {
        regionSelect.addEventListener('change', function () {
            if (this.value) {
                populateDistricts(this.value);
            } else {
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

    const districtSelect = document.getElementById('district');
    if (districtSelect) {
        districtSelect.addEventListener('change', function () {
            if (this.value) {
                populateWards(this.value);
            }
        });
    }
});
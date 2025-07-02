// ============================================
// ROPHIM-STYLE MOVIE RECOMMENDATION SYSTEM
// ============================================

// API Base URL
const API_BASE = 'http://127.0.0.1:5000';

// Global variables
let currentUser = 1;
let allMovies = [];

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    loadInitialData();
    
    // Header scroll effect
    window.addEventListener('scroll', function() {
        const header = document.querySelector('.netflix-header');
        if (window.scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
    });
});
document.getElementById('userSelect').addEventListener('change', function () {
    currentUser = parseInt(this.value);
    clearData(); // Xóa dữ liệu cũ của user trước
    loadInitialData(); // Load lại phim
    if (document.getElementById('social').classList.contains('active')) {
        loadUserComments();
        loadUserShares();
    }
});
// Load initial data for home page
function loadInitialData() {
    loadMovies();
    loadFeaturedMovies();
    loadTrendingMovies();
}

// Tab Management (RoPhim style)
function showTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all nav items
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => item.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    
    // Add active class to clicked nav item
    event.target.classList.add('active');
    
    // Load data based on tab
    switch(tabName) {
        case 'home':
            if (allMovies.length === 0) loadInitialData();
            break;
        case 'movies':
            if (allMovies.length === 0) loadMovies();
            break;
        case 'social':
            loadUserComments();
            loadUserShares();
            break;
    }
}

// Clear all data when user changes
function clearData() {
    document.getElementById('moviesList').innerHTML = '';
    document.getElementById('recommendationsList').innerHTML = '';
    document.getElementById('userCommentsList').innerHTML = '';
    document.getElementById('userSharesList').innerHTML = '';
    document.getElementById('popularSharesList').innerHTML = '';
    document.getElementById('featuredMovies').innerHTML = '';
    document.getElementById('trendingMovies').innerHTML = '';
    allMovies = [];
}

// RoPhim-style toast notification
function showToast(message, isError = false) {
    const toast = document.getElementById('toast');
    const icon = toast.querySelector('.toast-icon');
    const messageEl = toast.querySelector('.toast-message');
    
    messageEl.textContent = message;
    
    if (isError) {
        icon.className = 'toast-icon fas fa-exclamation-circle';
        icon.style.color = '#ef4444';
    } else {
        icon.className = 'toast-icon fas fa-check-circle';
        icon.style.color = 'var(--rophim-orange)';
    }
    
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}

// Show loading spinner
function showLoading(containerId) {
    document.getElementById(containerId).innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;
}

// API Functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(API_BASE + endpoint, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'Something went wrong');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showToast(error.message, true);
        throw error;
    }
}

// Load all movies
async function loadMovies() {
    showLoading('moviesList');
    
    try {
        const response = await apiCall('/movies/');
        allMovies = response.movies || [];
        displayMovies(allMovies, 'moviesList');
    } catch (error) {
        document.getElementById('moviesList').innerHTML = `
            <div class="error">Không thể tải danh sách phim. Vui lòng thử lại!</div>
        `;
    }
}

// Load featured movies for home page
async function loadFeaturedMovies() {
    try {
        const response = await apiCall('/movies/');
        const movies = response.movies || [];
        const featured = movies.slice(0, 10); // Get first 10 movies as featured
        displayRoPhimSlider(featured, 'featuredMovies');
    } catch (error) {
        document.getElementById('featuredMovies').innerHTML = `
            <div class="error">Không thể tải phim nổi bật</div>
        `;
    }
}

// Load trending movies for home page  
async function loadTrendingMovies() {
    try {
        const response = await apiCall('/movies/');
        const movies = response.movies || [];
        const trending = movies.slice(10, 20); // Get next 10 movies as trending
        displayRoPhimSlider(trending, 'trendingMovies');
    } catch (error) {
        document.getElementById('trendingMovies').innerHTML = `
            <div class="error">Không thể tải phim xu hướng</div>
        `;
    }
}

// Display movies in RoPhim slider format
function displayRoPhimSlider(movies, containerId) {
    const container = document.getElementById(containerId);
    
    if (movies.length === 0) {
        container.innerHTML = '<div class="no-data">Không có phim nào!</div>';
        return;
    }
    
    container.innerHTML = movies.map(movie => `
        <div class="netflix-card" onclick="showMovieDetails(${movie.movieId})">
            <div class="movie-poster">
                <i class="fas fa-film"></i>
            </div>
            <div class="card-overlay">
                <h3>${movie.title}</h3>
                <p>${movie.genres}</p>
                <div class="card-actions">
                    <button class="btn-netflix primary" onclick="event.stopPropagation(); rateMovie(${movie.movieId})">
                        <i class="fas fa-star"></i>
                    </button>
                    <button class="btn-netflix secondary" onclick="event.stopPropagation(); shareMovie(${movie.movieId})">
                        <i class="fas fa-share"></i>
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    addWordBreakToGenres();
}

// Display movies in grid format
function displayMovies(movies, containerId = 'moviesList') {
    const container = document.getElementById(containerId);
    
    if (movies.length === 0) {
        container.innerHTML = '<div class="no-data">Không có phim nào!</div>';
        return;
    }
    
    container.innerHTML = movies.map(movie => `
        <div class="movie-card" onclick="showMovieDetails(${movie.movieId})">
            <div class="movie-info">
                <div class="movie-title">${movie.title}</div>
                <div class="movie-genres">
                    <i class="fas fa-tags"></i> ${movie.genres}
                </div>
                <div class="movie-actions-row">
                    <div class="movie-actions">
                        <button class="btn-netflix primary" onclick="event.stopPropagation(); showMovieDetails(${movie.movieId})">
                            <i class="fas fa-info-circle"></i>
                        </button>
                        <button class="btn-netflix warning" onclick="event.stopPropagation(); shareMovie(${movie.movieId})">
                            <i class="fas fa-share"></i>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
    addWordBreakToGenres();
}

// Filter movies
function filterMovies() {
    const searchTerm = document.getElementById('movieSearch').value.toLowerCase();
    const filteredMovies = allMovies.filter(movie => 
        movie.title.toLowerCase().includes(searchTerm) ||
        movie.genres.toLowerCase().includes(searchTerm)
    );
    displayMovies(filteredMovies);
}

// Rate a movie (quick rating without modal)
async function rateMovieQuick(movieId) {
    const ratingValue = document.getElementById(`rating-${movieId}`).value;
    
    if (!ratingValue) {
        showToast('Vui lòng chọn điểm đánh giá!', true);
        return;
    }
    
    try {
        await apiCall('/ratings/rate', 'POST', {
            userId: currentUser.toString(),
            movieId: movieId.toString(),
            rating: ratingValue
        });
        
        showToast('Đánh giá thành công! 🎉');
        document.getElementById(`rating-${movieId}`).value = '';
    } catch (error) {
        // Error already handled by apiCall
    }
}

// Rate a movie (for slider cards) - use same RoPhim modal
async function rateMovie(movieId) {
    rateMovieInModal(movieId);
}

// Get recommendations
// Get recommendations - Updated to handle the correct JSON format
async function getRecommendations() {
    showLoading('recommendationsList');
    
    try {
        const response = await apiCall(`/recommendations/${currentUser}`);
        const recommendations = response.recommendations || [];
        
        if (recommendations.length === 0) {
            document.getElementById('recommendationsList').innerHTML = `
                <div class="no-data">Không có gợi ý phim nào cho bạn. Hãy đánh giá thêm một số phim!</div>
            `;
            return;
        }
        
        // Map the recommendations to include genre information from allMovies
        const recommendedMovies = recommendations.map(rec => {
            // Find the full movie info from allMovies array
            const fullMovie = allMovies.find(m => m.movieId === rec.movieId);
            return {
                movieId: rec.movieId,
                title: rec.title,
                genres: fullMovie ? fullMovie.genres : 'N/A' // Use genres from allMovies or fallback
            };
        });
        
        displayRecommendations(recommendedMovies);
    } catch (error) {
        document.getElementById('recommendationsList').innerHTML = `
            <div class="error">Không thể lấy gợi ý phim. Vui lòng thử lại!</div>
        `;
    }
}

// Display recommendations
function displayRecommendations(movies) {
    const container = document.getElementById('recommendationsList');
    
    if (movies.length === 0) {
        container.innerHTML = '<div class="no-data">Không có gợi ý phim nào!</div>';
        return;
    }
    
    container.innerHTML = movies.map(movie => `
        <div class="movie-card recommended" onclick="showMovieDetails(${movie.movieId})">
            <div class="movie-poster">
                <i class="fas fa-magic" style="color: gold;"></i>
            </div>
            <div class="movie-info">
                <div class="movie-title">
                    <i class="fas fa-star" style="color: gold; margin-right: 5px;"></i>
                    ${movie.title}
                </div>
                <div class="movie-genres">
                    <i class="fas fa-tags"></i> ${movie.genres}
                </div>
                <div class="movie-actions">
                    <button class="btn-netflix primary" onclick="event.stopPropagation(); showMovieDetails(${movie.movieId})">
                        <i class="fas fa-info-circle"></i> Chi tiết
                    </button>
                    <button class="btn-netflix warning" onclick="event.stopPropagation(); shareMovie(${movie.movieId})">
                        <i class="fas fa-share"></i> Chia sẻ
                    </button>
                </div>
            </div>
        </div>
    `).join('');
    addWordBreakToGenres();
}

// Show movie details in RoPhim-style modal
async function showMovieDetails(movieId) {
    try {
        const movie = allMovies.find(m => m.movieId === movieId);
        if (!movie) {
            showToast('Không tìm thấy thông tin phim!', true);
            return;
        }
        
        // Load movie comments
        const commentsResponse = await apiCall(`/comments/movie/${movieId}`);
        const comments = commentsResponse.comments || [];
        
        const modalContent = `
            <div class="movie-details-layout">

                <div class="movie-details-info">
                    <h2 class="movie-details-title">
                        <i class="fas fa-clapperboard"></i> ${movie.title}
                    </h2>
                    <div class="movie-details-meta">
                        <span class="movie-details-genres"><i class="fas fa-tags"></i> ${movie.genres}</span>
                        <span class="movie-details-year">Năm: ${movie.title.match(/\((\d{4})\)/) ? movie.title.match(/\((\d{4})\)/)[1] : ''}</span>
                        <span class="movie-details-id">ID: <b>${movie.movieId}</b></span>
                    </div>
                    <div class="movie-details-actions">
                        <button class="btn-hero primary" onclick="rateMovieInModal(${movieId})">
                            <i class="fas fa-star"></i> Đánh giá
                        </button>
                        <button class="btn-hero secondary" onclick="shareMovie(${movieId})">
                            <i class="fas fa-share"></i> Chia sẻ
                        </button>
                    </div>
                    <div class="movie-details-comments-block">
                        <h3><i class="fas fa-comments"></i> Bình luận (${comments.length})</h3>
                        <div class="movie-details-add-comment">
                            <textarea id="newComment" placeholder="Viết bình luận của bạn..."></textarea>
                            <button class="btn-netflix primary" onclick="addComment(${movieId})">
                                <i class="fas fa-comment"></i> Thêm bình luận
                            </button>
                        </div>
                        <div class="comments-list movie-details-comments-list">
                            ${comments.map(comment => `
                                <div class="comment-item">
                                    <div class="comment-header">
                                        <strong>${comment.username}</strong>
                                        <span>${new Date(comment.created_at).toLocaleString()}</span>
                                    </div>
                                    <div class="comment-content">${comment.content}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('movieDetails').innerHTML = modalContent;
        document.getElementById('movieModal').classList.add('show');
        document.getElementById('movieModal').style.display = 'flex';
        
    } catch (error) {
        showToast('Không thể tải chi tiết phim!', true);
    }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('movieModal');
    modal.classList.remove('show');
    modal.classList.add('hide');
    setTimeout(() => {
        modal.style.display = 'none';
        modal.classList.remove('hide');
    }, 250);
}

// Rate movie in modal with RoPhim-style UI
function rateMovieInModal(movieId) {
    const movie = allMovies.find(m => m.movieId === movieId);
    if (!movie) {
        showToast('Không tìm thấy phim!', true);
        return;
    }

    // Create rating modal HTML
    const ratingModalHTML = `
        <div id="ratingModal" class="netflix-modal show" style="display: flex;">
            <div class="modal-backdrop" onclick="closeRatingModal()"></div>
            <div class="modal-content" style="max-width: 400px;">
                <button class="modal-close" onclick="closeRatingModal()">
                    <i class="fas fa-times"></i>
                </button>
                <div class="rating-modal-content">
                    <h2><i class="fas fa-star"></i> Đánh giá phim</h2>
                    <p class="movie-title-rating">${movie.title}</p>
                    <p class="movie-genres-rating">${movie.genres}</p>
                    
                    <div class="star-rating">
                        <div class="star-rating-label">Chọn số sao:</div>
                        <div class="stars-container">
                            <span class="star" data-rating="1" onclick="selectRating(1, ${movieId})">
                                <i class="fas fa-star"></i>
                            </span>
                            <span class="star" data-rating="2" onclick="selectRating(2, ${movieId})">
                                <i class="fas fa-star"></i>
                            </span>
                            <span class="star" data-rating="3" onclick="selectRating(3, ${movieId})">
                                <i class="fas fa-star"></i>
                            </span>
                            <span class="star" data-rating="4" onclick="selectRating(4, ${movieId})">
                                <i class="fas fa-star"></i>
                            </span>
                            <span class="star" data-rating="5" onclick="selectRating(5, ${movieId})">
                                <i class="fas fa-star"></i>
                            </span>
                        </div>
                        <div class="rating-text">Nhấn vào sao để đánh giá</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', ratingModalHTML);
    
    // Add star hover effects
    addStarHoverEffects();
}

// Close rating modal
function closeRatingModal() {
    const ratingModal = document.getElementById('ratingModal');
    if (ratingModal) {
        ratingModal.remove();
    }
}

// Select rating and submit
async function selectRating(rating, movieId) {
    try {
        await apiCall('/ratings/rate', 'POST', {
            userId: currentUser.toString(),
            movieId: movieId.toString(),
            rating: rating.toString()
        });
        
        showToast(`Đã đánh giá ${rating} sao! 🎉`);
        closeRatingModal();
        
    } catch (error) {
        // Error already handled by apiCall
    }
}

// Add star hover effects
function addStarHoverEffects() {
    const stars = document.querySelectorAll('.star');
    const ratingText = document.querySelector('.rating-text');
    const starsContainer = document.querySelector('.stars-container');
    
    stars.forEach((star, index) => {
        star.addEventListener('mouseenter', () => {
            // Set rating level for color
            starsContainer.setAttribute('data-rating', index + 1);
            
            // Light up stars up to hovered star
            for (let i = 0; i <= index; i++) {
                stars[i].classList.add('hovered');
            }
            // Clear stars after hovered star
            for (let i = index + 1; i < stars.length; i++) {
                stars[i].classList.remove('hovered');
            }
            
            // Update text with emojis
            const ratings = ['😞 Tệ', '😐 Không hay', '😊 Tạm được', '😍 Hay', '🤩 Tuyệt vời'];
            ratingText.textContent = `${index + 1} sao - ${ratings[index]}`;
        });
        
        star.addEventListener('mouseleave', () => {
            // Reset text
            ratingText.textContent = 'Nhấn vào sao để đánh giá';
        });
    });
    
    // Reset all stars when leaving the container
    starsContainer.addEventListener('mouseleave', () => {
        stars.forEach(star => star.classList.remove('hovered'));
        starsContainer.removeAttribute('data-rating');
        ratingText.textContent = 'Nhấn vào sao để đánh giá';
    });
}

// Add comment
async function addComment(movieId) {
    const content = document.getElementById('newComment').value.trim();
    
    if (!content) {
        showToast('Vui lòng nhập nội dung bình luận!', true);
        return;
    }
    
    try {
        await apiCall('/comments/add', 'POST', {
            userId: currentUser,
            movieId: movieId,
            content: content
        });
        
        showToast('Thêm bình luận thành công! 💬');
        document.getElementById('newComment').value = '';
        
        // Reload movie details
        showMovieDetails(movieId);
        
    } catch (error) {
        // Error already handled by apiCall
    }
}

// Share movie with better UI
async function shareMovie(movieId) {
    const movie = allMovies.find(m => m.movieId === movieId);
    if (!movie) {
        showToast('Không tìm thấy phim!', true);
        return;
    }

    // Create share modal HTML
    const shareModalHTML = `
        <div id="shareModal" class="netflix-modal show" style="display: flex;">
            <div class="modal-backdrop" onclick="closeShareModal()"></div>
            <div class="modal-content" style="max-width: 500px;">
                <button class="modal-close" onclick="closeShareModal()">
                    <i class="fas fa-times"></i>
                </button>
                <div class="share-modal-content">
                    <h2><i class="fas fa-share-alt"></i> Chia sẻ phim</h2>
                    <p class="movie-title-share">${movie.title}</p>
                    <p class="movie-genres-share">${movie.genres}</p>
                    
                    <div class="share-platforms">
                        <button class="share-platform-btn" onclick="shareToStyle('facebook', ${movieId})">
                            <i class="fab fa-facebook-f"></i>
                            <span>Facebook</span>
                        </button>
                        <button class="share-platform-btn" onclick="shareToStyle('twitter', ${movieId})">
                            <i class="fab fa-twitter"></i>
                            <span>Twitter</span>
                        </button>
                        <button class="share-platform-btn" onclick="shareToStyle('email', ${movieId})">
                            <i class="fas fa-envelope"></i>
                            <span>Email</span>
                        </button>
                        <button class="share-platform-btn" onclick="shareToStyle('whatsapp', ${movieId})">
                            <i class="fab fa-whatsapp"></i>
                            <span>WhatsApp</span>
                        </button>
                        <button class="share-platform-btn" onclick="shareToStyle('telegram', ${movieId})">
                            <i class="fab fa-telegram"></i>
                            <span>Telegram</span>
                        </button>
                        <button class="share-platform-btn" onclick="shareToStyle('link', ${movieId})">
                            <i class="fas fa-link"></i>
                            <span>Copy Link</span>
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Add modal to body
    document.body.insertAdjacentHTML('beforeend', shareModalHTML);
}

// Close share modal
function closeShareModal() {
    const shareModal = document.getElementById('shareModal');
    if (shareModal) {
        shareModal.remove();
    }
}

// Share to specific platform
async function shareToStyle(platform, movieId) {
    try {
        const response = await apiCall('/shares/share', 'POST', {
            userId: currentUser,
            movieId: movieId,
            platform: platform
        });
        
        showToast(`Chia sẻ phim "${response.movieTitle}" lên ${platform} thành công! 🚀`);
        closeShareModal();
        
    } catch (error) {
        // Error already handled by apiCall
    }
}

// Load user comments
async function loadUserComments() {
    showLoading('userCommentsList');
    
    try {
        const response = await apiCall(`/comments/user/${currentUser}`);
        const comments = response.comments || [];
        
        const container = document.getElementById('userCommentsList');
        
        if (comments.length === 0) {
            container.innerHTML = '<div class="no-data">Bạn chưa có bình luận nào!</div>';
            return;
        }
        
        container.innerHTML = comments.map(comment => `
            <div class="comment-item" style="margin-bottom: 18px;">
                <div class="comment-header">
                    <strong>${comment.movieTitle}</strong>
                    <span>${new Date(comment.created_at).toLocaleString()}</span>
                </div>
                <div class="comment-content">${comment.content}</div>
            </div>
        `).join('');
        
    } catch (error) {
        document.getElementById('userCommentsList').innerHTML = `
            <div class="error">Không thể tải bình luận. Vui lòng thử lại!</div>
        `;
    }
}

// Delete comment
async function deleteComment(commentId) {
    if (!confirm('Bạn có chắc chắn muốn xóa bình luận này?')) return;
    
    try {
        await apiCall(`/comments/delete/${commentId}`, 'DELETE');
        showToast('Xóa bình luận thành công! 🗑️');
        loadUserComments();
    } catch (error) {
        // Error already handled by apiCall
    }
}

// Load user shares
async function loadUserShares() {
    showLoading('userSharesList');
    
    try {
        const response = await apiCall(`/shares/user/${currentUser}/shares`);
        const shares = response.shares || [];
        
        const container = document.getElementById('userSharesList');
        
        if (shares.length === 0) {
            container.innerHTML = '<div class="no-data">Bạn chưa chia sẻ phim nào!</div>';
            return;
        }
        
        container.innerHTML = shares.map(share => `
            <div class="share-item">
                <div class="share-header">
                    <strong>${share.movieTitle}</strong>
                    <span class="share-date">${new Date(share.shared_at).toLocaleString()}</span>
                </div>
                <div class="share-platform">
                    <i class="fas fa-share-alt"></i>
                    Đã chia sẻ lên: <b>${share.platform}</b>
                </div>
            </div>
        `).join('');
    } catch (error) {
        document.getElementById('userSharesList').innerHTML = `
            <div class="error">Không thể tải danh sách chia sẻ. Vui lòng thử lại!</div>
        `;
    }
}

// Load popular shared movies
async function loadPopularShares() {
    showLoading('popularSharesList');
    try {
        const response = await apiCall('/shares/popular');
        const popularMovies = response.popularMovies || [];
        const container = document.getElementById('popularSharesList');
        container.classList.add('popular-shares-grid');
        if (popularMovies.length === 0) {
            container.innerHTML = '<div class="no-data">Chưa có phim nào được chia sẻ!</div>';
            return;
        }
        container.innerHTML = popularMovies.map(movie => `
            <div class="popular-shares-card" onclick="showMovieDetails(${movie.movieId})">
                <div class="popular-shares-poster">
                    <i class="fas fa-fire"></i>
                </div>
                <div class="popular-shares-info">
                    <div class="popular-shares-title">${movie.movieTitle}</div>
                    <div class="popular-shares-genres"><i class="fas fa-tags"></i> ${movie.genres}</div>
                    <div class="popular-shares-count">
                        <i class="fas fa-share-alt"></i> Được chia sẻ: <b>${movie.shareCount}</b> lần
                    </div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        document.getElementById('popularSharesList').innerHTML = `
            <div class="error">Không thể tải thống kê phim hot. Vui lòng thử lại!</div>
        `;
    }
}

// Tự động chèn <wbr> sau mỗi dấu | để genres xuống dòng đẹp
function addWordBreakToGenres() {
    // Cho movie card grid
    document.querySelectorAll('.movie-genres').forEach(function(el) {
        el.innerHTML = el.textContent.replace(/\|/g, ' |<wbr>');
    });
    // Cho card overlay trong slider
    document.querySelectorAll('.card-overlay p').forEach(function(el) {
        el.innerHTML = el.textContent.replace(/\|/g, ' |<wbr>');
    });
}
// Gọi hàm này mỗi khi render phim xong
// Patch cho home, movies, recommendations
const origDisplayMovies = displayMovies;
displayMovies = function() {
    origDisplayMovies.apply(this, arguments);
    addWordBreakToGenres();
};
const origDisplayRoPhimSlider = displayRoPhimSlider;
displayRoPhimSlider = function() {
    origDisplayRoPhimSlider.apply(this, arguments);
    addWordBreakToGenres();
};
const origDisplayRecommendations = displayRecommendations;
displayRecommendations = function() {
    origDisplayRecommendations.apply(this, arguments);
    addWordBreakToGenres();
};
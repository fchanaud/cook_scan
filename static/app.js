const API_URL = window.location.origin;

new Vue({
    el: '#app',
    vuetify: new Vuetify(),
    delimiters: ['[[', ']]'],
    data: {
        files: [],
        recipes: [],
        loading: false,
        progress: 0,
        error: null
    },
    methods: {
        handleFileSelect(files) {
            this.files = files;
        },
        async uploadImages() {
            if (!this.files.length) return;

            this.loading = true;
            this.progress = 0;
            this.error = null;

            const formData = new FormData();
            this.files.forEach(file => {
                formData.append('files', file);
            });

            try {
                const response = await axios.post(`${API_URL}/analyze-images/`, formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    },
                    onUploadProgress: (progressEvent) => {
                        this.progress = Math.round(
                            (progressEvent.loaded * 100) / progressEvent.total
                        );
                    }
                });

                this.recipes = response.data;
            } catch (error) {
                this.error = error.response?.data?.detail || 
                    'Error processing images. Please try again.';
                console.error('Upload error:', error);
            } finally {
                this.loading = false;
            }
        }
    }
}); 
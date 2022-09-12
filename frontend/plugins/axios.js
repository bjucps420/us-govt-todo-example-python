export default function ({ $axios }) {
  $axios.onRequest(config => {
    if(config.method === 'post') {
      return $axios.get(`/api/auth/get-csrf`).then((response) => {
        config.headers.common['x-csrftoken'] = response.headers['x-csrftoken'];
        return config;
      });
    }
  })
}

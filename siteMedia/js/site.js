function showProgressDiv() {
  progressDiv = document.getElementById('progress')
  innerProgressDiv = document.getElementById('progress2')
  progressDiv.style.height = document.documentElement.scrollHeight + "px"
  innerProgressDiv.style.top = (parseInt(document.documentElement.scrollTop) + parseInt(document.documentElement.clientHeight) / 2 - 36) + "px"
  progressDiv.style.display = 'block'
  innerProgressDiv.style.display = 'block'
}


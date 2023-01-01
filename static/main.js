const backtotopButton = document.querySelector(".back_to_top");
document.querySelector(".back_to_top").addEventListener('click', gotoTop);
window.onscroll = scrollFunction;
function scrollFunction(){
    if (document.body.scrollTop > 50 || document.documentElement.scrollTop > 50)
    {
        backtotopButton.style.visibility = "visible";
    }
    else
    {
        backtotopButton.style.visibility = "hidden";
    }

}

function gotoTop(){
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}

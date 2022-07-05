using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class Timer : MonoBehaviour
{
    public Text timer;

    float seconds, minutes;

    float timeSinceStarted = 0;
    bool canStartCoroutine = true;
    // Start is called before the first frame update
    void Start()
    {
        minutes = 10;
        seconds = 5;
        timer.text = minutes.ToString("00") + ":" + seconds.ToString("00");
        StartCoroutine(hideTimer());
    }

    // Update is called once per frame
    void Update()
    {
        seconds -= Time.deltaTime;
        if(seconds <= 0 && minutes > 0)
        {
            minutes -= 1;
            seconds = 60;
        }
        timer.text = minutes.ToString("00") + ":" + ((int)seconds % 60).ToString("00");

        if((minutes == 8 || minutes == 4 || minutes == 1) && canStartCoroutine)
        {
            canStartCoroutine = false;
            StartCoroutine(showTimer());
        }
    }

    IEnumerator hideTimer()
    {
        yield return new WaitForSeconds(20);
        while (timer.gameObject.GetComponent<CanvasGroup>().alpha > 0)
        {
            timer.gameObject.GetComponent<CanvasGroup>().alpha -= 0.0002f;
            yield return new WaitForEndOfFrame();
        }
    }

    IEnumerator showTimer()
    {
        while(timer.gameObject.GetComponent<CanvasGroup>().alpha < 1)
        {
            timer.gameObject.GetComponent<CanvasGroup>().alpha += 0.0002f;
            yield return new WaitForEndOfFrame();
        }
        yield return new WaitForSeconds(3);
        timer.gameObject.GetComponent<CanvasGroup>().alpha = 0;
        yield return new WaitForSeconds(1f);
        timer.gameObject.GetComponent<CanvasGroup>().alpha = 1;
        yield return new WaitForSeconds(1f);
        timer.gameObject.GetComponent<CanvasGroup>().alpha = 0;
        yield return new WaitForSeconds(1f);
        timer.gameObject.GetComponent<CanvasGroup>().alpha = 1;
        yield return new WaitForSeconds(1f);
        timer.gameObject.GetComponent<CanvasGroup>().alpha = 0;
        yield return new WaitForSeconds(1f);
        timer.gameObject.GetComponent<CanvasGroup>().alpha = 1;
        yield return new WaitForSeconds(1f);
        timer.gameObject.GetComponent<CanvasGroup>().alpha = 0;
        yield return new WaitForSeconds(1f);
        timer.gameObject.GetComponent<CanvasGroup>().alpha = 1;
        yield return new WaitForSeconds(1f);
        timer.gameObject.GetComponent<CanvasGroup>().alpha = 0;
        yield return new WaitForSeconds(1f);

        yield return new WaitForSeconds(55);
        canStartCoroutine = true;
    }
}

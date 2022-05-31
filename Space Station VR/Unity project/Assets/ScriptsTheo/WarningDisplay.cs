using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WarningDisplay : MonoBehaviour
{
    public CanvasGroup cg_text;
    // Start is called before the first frame update
    void Start()
    {
        StartCoroutine(hideText());

    }

    private void Update()
    {
        /*
        if(cg_text.alpha == 1)
        {
            Debug.Log("hide");
            StartCoroutine(hideText());
            StopCoroutine(displayText());
        }
        else if(cg_text.alpha == 0)
        {
            Debug.Log("display");
            StartCoroutine(displayText());
            StopCoroutine(hideText());
        }
        */
    }

    private IEnumerator displayText()
    {
        while (cg_text.alpha < 1f)
        {
            cg_text.alpha += 0.01f;
            yield return new WaitForEndOfFrame();
        }
        yield return new WaitForSeconds(0.5f);
        StartCoroutine(hideText());
    }

    private IEnumerator hideText()
    {
        while (cg_text.alpha > 0f)
        {
            cg_text.alpha -= 0.01f;
            yield return new WaitForEndOfFrame();
        }
        StartCoroutine(displayText());
    }


}
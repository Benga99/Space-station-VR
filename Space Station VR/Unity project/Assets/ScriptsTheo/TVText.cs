using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

public class TVText : MonoBehaviour
{
    [SerializeField]
    private Text textField;
    [SerializeField]
    private int numbering;

    bool start;
    int randomNum;
    Rotateable rotateable;

    // Start is called before the first frame update
    void Start()
    {
        rotateable = FindObjectOfType<Rotateable>();
    }

    /*
    void Update()
    {
        
        if (start)
        {
            StartCoroutine(displayingNumbers());
            start = false;
        }
        
    }


    public void setStart(bool s)
    {
        start = s;
    }
    */
    public IEnumerator displayingNumbers()
    {
        float seconds = 0.00001f;
        while (seconds < 1f)
        {
            randomNum = Random.Range(1, 13);
            textField.text = randomNum.ToString();
            yield return new WaitForSeconds(seconds);
            seconds *= 1.075f;
            Debug.Log(seconds);
        }

        rotateable.solution[numbering] = randomNum;
    }
}

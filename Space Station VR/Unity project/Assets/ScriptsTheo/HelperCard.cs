using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class HelperCard : MonoBehaviour
{
    [SerializeField]
    private GameObject HelpCard1;
    [SerializeField]
    private GameObject HelpCard2;
    [SerializeField]
    private GameObject HelpCard3;

    public bool showCard1 = false;
    public bool showCard2 = false;
    public bool showCard3 = false;

    private bool card1revealed = false;
    private bool card2revealed = false;
    private bool card3revealed = false;

    private Vector3 positionForCard = new Vector3();
    private Vector3 finalRotation = new Vector3();

    // Start is called before the first frame update
    void Start()
    {
        
    }

    // Update is called once per frame
    void Update()
    {
        if (showCard1 && !card1revealed)
        {
            card1revealed = true;
            StartCoroutine(showCard(HelpCard1));
        }
        if (showCard2 && !card2revealed)
        {
            card2revealed = true;
            StartCoroutine(showCard(HelpCard2));
        }
        if (showCard3 && !card3revealed)
        {
            card3revealed = true;
            StartCoroutine(showCard(HelpCard3));
        }
    }


    IEnumerator showCard(GameObject card)
    {
        Vector3 initialPos = card.transform.position;
        Vector3 initialRot = card.transform.localEulerAngles;
        float i = 0;
        while (i < 1)
        {
            card.transform.position = Vector3.Lerp(initialPos, positionForCard, i);
            //card.transform.rotation = 



            i += Time.deltaTime;
        }
        yield return new WaitForEndOfFrame();
    }
}
